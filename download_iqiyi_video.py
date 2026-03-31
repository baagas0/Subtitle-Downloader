#!/usr/bin/env python3
"""
iQIYI Video Downloader
Download video dari iQIYI (iq.com) menggunakan DASH API

Based on analysis of iQIYI subtitle downloader project
"""

import os
import sys
import subprocess
import http.cookiejar as cookiejar
import requests
import re
import orjson
from hashlib import md5
from time import time, sleep
from urllib.parse import urlencode, urljoin
import json

class IQIYIVideoDownloader:
    def __init__(self, cookie_file='cookies/www.iq.com_cookies.txt'):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Referer': 'https://www.iq.com/'
        })

        # Load cookies
        cj = cookiejar.MozillaCookieJar(cookie_file)
        cj.load(ignore_discard=True, ignore_expires=True)
        for cookie in cj:
            self.session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)

        self.cookies = {
            '__dfp': self.session.cookies.get_dict().get('__dfp', ''),
            'P00003': self.session.cookies.get_dict().get('P00003', '0'),
            'QC005': self.session.cookies.get_dict().get('QC005', ''),
        }

    def get_auth_key(self, tvid):
        """Generate authKey for DASH request"""
        text = f"d41d8cd98f00b204e9800998ecf8427e{int(time() * 1000)}{tvid}"
        md = md5()
        md.update(text.encode())
        return md.hexdigest()

    def get_vid_from_play_page(self, play_url):
        """Extract vid and tvid from play page HTML"""
        print(f"[1] Fetching play page: {play_url}")
        res = self.session.get(play_url, timeout=10)

        if not res.ok:
            raise Exception(f"Failed to fetch play page: {res.status_code}")

        # Extract React props from HTML
        match = re.search(r'({"props":{.*})', res.text)
        if not match:
            raise Exception("Could not find React props in HTML")

        data = orjson.loads(match.group(1))
        curVideoInfo = data['props']['initialState']['play']['curVideoInfo']

        vid = curVideoInfo['vid']
        tvid = curVideoInfo.get('tvId') or curVideoInfo.get('qipuId', '')

        print(f"[2] Extracted IDs:")
        print(f"     vid: {vid}")
        print(f"     tvid: {tvid}")

        return vid, tvid

    def generate_dash_url(self, vid, tvid):
        """Generate complete DASH URL with vf parameter"""
        print("\n[3] Generating DASH URL...")

        # Build parameters
        params = {
            "tvid": tvid,
            "bid": "",
            "vid": vid,
            "src": "01011021010010000000",
            "vt": "0",
            "rs": "1",
            "uid": self.cookies['P00003'],
            "ori": "pcw",
            "ps": "0",
            "k_uid": self.cookies['QC005'],
            "pt": "0",
            "d": "0",
            "s": "",
            "lid": "",
            "slid": "0",
            "cf": "",
            "ct": "",
            "authKey": self.get_auth_key(tvid),
            "k_tag": "1",
            "ost": "0",
            "ppt": "0",
            "dfp": self.cookies['__dfp'],
            "locale": "zh_cn",
            "prio": '{"ff":"","code":}',
            "k_err_retries": "0",
            "qd_v": "2",
            "tm": int(time() * 1000),
            "qdy": "a",
            "qds": "0",
            "k_ft1": "143486267424900",
            "k_ft4": "1581060",
            "k_ft7": "4",
            "k_ft5": "1",
            "bop": '{"version":"10.0","dfp":""}',
            "ut": "1",
        }

        url = "/dash?" + urlencode(params)

        # Execute cmd5x.js to get vf parameter
        cmdx5js = os.path.join(os.path.dirname(__file__), 'services/iqiyi/cmd5x.js')

        try:
            executable = os.path.exists('/usr/local/bin/node') and '/usr/local/bin/node' or 'node'
            process = subprocess.run(
                [executable, cmdx5js, url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10
            )
            vf = process.stdout.decode("utf-8").strip()
        except Exception as e:
            raise Exception(f"Failed to execute cmd5x.js: {e}")

        dash_url = f"https://cache-video.iq.com{url}&vf={vf}"
        print(f"[4] DASH URL generated (length: {len(dash_url)})")

        return dash_url

    def get_dash_manifest(self, dash_url):
        """Fetch DASH manifest and extract video streams"""
        print("\n[5] Fetching DASH manifest...")

        res = self.session.get(dash_url, timeout=15)

        if not res.ok:
            raise Exception(f"Failed to fetch DASH manifest: {res.status_code}")

        data = res.json()

        if 'data' not in data or 'program' not in data['data']:
            raise Exception("Invalid DASH response structure")

        program = data['data']['program']

        print(f"[6] Analyzing DASH response...")

        # Extract video streams
        videos = program.get('video', [])
        audios = program.get('audio', [])

        print(f"\n     Found {len(videos)} video streams")
        print(f"     Found {len(audios)} audio streams")

        return {
            'videos': videos,
            'audios': audios,
            'full_data': data
        }

    def get_best_video_stream(self, videos):
        """Select best quality video stream"""
        print("\n[7] Selecting best video quality...")

        # Sort by bitrate/quality
        # Usually first video is highest quality
        best = videos[0]

        # Get metadata
        vsize = best.get('vsize', 0)
        br = best.get('br', 0)
        width = best.get('bid', 0)
        ff = best.get('ff', 'unknown')

        print(f"     Format: {ff}")
        print(f"     Size: {vsize / (1024**3):.2f} GB" if vsize > 0 else "     Size: Unknown")
        print(f"     Width: {width}")
        print(f"     Bitrate: {br}")

        # Get manifest path
        manifest_path = best.get('mu', '')
        if not manifest_path:
            raise Exception("No manifest path (mu) found in video stream")

        print(f"     Manifest path: {manifest_path}")

        return best, manifest_path

    def parse_dash_xml(self, xml_path):
        """Parse iQIYI DASH XML manifest"""
        print(f"\n[8] Fetching DASH XML manifest: {xml_path}")

        url = f"https://meta.video.iqiyi.com{xml_path}"
        res = self.session.get(url, timeout=15)

        if not res.ok:
            raise Exception(f"Failed to fetch XML manifest: {res.status_code}")

        # Save for analysis
        with open('video_manifest.xml', 'w') as f:
            f.write(res.text)

        print(f"[9] XML manifest saved to video_manifest.xml")
        print(f"     Size: {len(res.text)} bytes")

        # Parse XML structure (iQIYI custom format)
        # The XML contains flv structure with segment information

        import xml.etree.ElementTree as ET
        root = ET.fromstring(res.text)

        # Find flv element
        flv = root.find('.//flv')
        if flv is None:
            raise Exception("Could not find flv element in XML")

        flv_name = flv.get('name')
        print(f"\n[10] FLV file name: {flv_name}")
        print(f"      This suggests the video is delivered as single FLV file")

        # Get video info
        width = root.find('.//width')
        height = root.find('.//height')

        if width is not None and height is not None:
            print(f"      Resolution: {width.text}x{height.text}")

        return {
            'flv_name': flv_name,
            'xml_content': res.text
        }

    def download_video_simple(self, video_url, output_path):
        """Simple download using requests (for direct video URLs)"""
        print(f"\n[11] Downloading video...")
        print(f"      URL: {video_url[:100]}...")
        print(f"      Output: {output_path}")

        response = self.session.get(video_url, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0))

        print(f"      Size: {total_size / (1024**3):.2f} GB")

        downloaded = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (10 * 1024 * 1024) == 0:  # Every 10MB
                        percent = (downloaded / total_size * 100) if total_size > 0 else 0
                        print(f"      Downloaded: {downloaded / (1024**2):.1f} MB ({percent:.1f}%)")

        print(f"[12] ✓ Download complete: {output_path}")

    def download(self, url, output_file=None):
        """Main download function"""
        try:
            # Step 1: Get vid and tvid
            vid, tvid = self.get_vid_from_play_page(url)

            # Step 2: Generate DASH URL
            dash_url = self.generate_dash_url(vid, tvid)

            # Step 3: Get DASH manifest
            manifest_data = self.get_dash_manifest(dash_url)

            # Step 4: Get best video stream
            best_video, manifest_path = self.get_best_video_stream(manifest_data['videos'])

            # Step 5: Parse DASH XML to understand delivery format
            xml_data = self.parse_dash_xml(manifest_path)

            # Save analysis data
            analysis = {
                'vid': vid,
                'tvid': tvid,
                'dash_url': dash_url,
                'manifest_path': manifest_path,
                'video_stream': best_video,
                'xml_data': xml_data,
            }

            with open('video_analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2, default=str)

            print(f"\n[✓] Analysis complete! Data saved to video_analysis.json")
            print(f"\n" + "="*80)
            print("IMPORTANT FINDING:")
            print("="*80)
            print("iQIYI delivers video using a custom DASH format.")
            print(f"Video is referenced as FLV: {xml_data['flv_name']}")
            print("\nThe DASH XML (video_manifest.xml) contains metadata but NOT direct segment URLs.")
            print("This suggests video segments are dynamically generated or encrypted.")
            print("\nTo download the actual video, you need to:")
            print("1. Use the XstreamDL_CLI tool in tools/ directory")
            print("2. Or build a custom HLS/DASH downloader that handles iQIYI's encryption")
            print("3. Or record the network traffic while playing in browser to get actual segment URLs")
            print("="*80)

            return analysis

        except Exception as e:
            print(f"\n[✗] Error: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_iqiyi_video.py <iqiyi_play_url>")
        print("Example: python3 download_iqiyi_video.py https://www.iq.com/play/the-best-thing-episode-1-yy4gnywufo?lang=id_id")
        sys.exit(1)

    url = sys.argv[1]

    downloader = IQIYIVideoDownloader()
    result = downloader.download(url)

    if result:
        print(f"\n✓ Analysis complete!")
        print(f"  Check video_analysis.json for detailed information")
        print(f"  Check video_manifest.xml for DASH manifest structure")

if __name__ == '__main__':
    main()
