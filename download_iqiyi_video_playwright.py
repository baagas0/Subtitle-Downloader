#!/usr/bin/env python3
"""
iQIYI Video Downloader using Playwright
Download video dari iQIYI (iq.com) dengan merekam network traffic

This script uses Playwright to:
1. Open iQIYI play page
2. Play the video
3. Record all network requests
4. Extract segment URLs (.ts, .m4s files)
5. Download all segments
6. Merge with ffmpeg into MP4
"""

import os
import sys
import asyncio
import http.cookiejar as cookiejar
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
import json
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Warning: Playwright not installed. Install with: pip install playwright")


class IQIYIPlaywrightDownloader:
    def __init__(self, cookie_file='cookies/www.iq.com_cookies.txt', output_dir='downloads'):
        self.cookie_file = cookie_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.segment_urls = []
        self.manifest_urls = []
        self.video_info = {}

        # Session untuk download segments
        self.session = requests.Session()
        self._load_cookies()

    def _load_cookies(self):
        """Load cookies untuk session requests"""
        try:
            cj = cookiejar.MozillaCookieJar(self.cookie_file)
            cj.load(ignore_discard=True, ignore_expires=True)

            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'Referer': 'https://www.iq.com/'
            })

            for cookie in cj:
                self.session.cookies.set(cookie.name, cookie.value,
                                       domain=cookie.domain, path=cookie.path)

            print(f"[✓] Cookies loaded from {self.cookie_file}")
        except Exception as e:
            print(f"[⚠️  Warning: Could not load cookies: {e}")

    def _convert_cookies_to_playwright(self):
        """Convert cookies file to Playwright format"""
        cookies = []
        try:
            cj = cookiejar.MozillaCookieJar(self.cookie_file)
            cj.load(ignore_discard=True, ignore_expires=True)

            for cookie in cj:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                })
        except Exception as e:
            print(f"[⚠️  Warning: Could not parse cookies: {e}")

        return cookies

    def extract_video_info(self, url):
        """Extract video info dari URL (tanpa Playwright)"""
        import re
        import orjson

        print("\n[1] Extracting video information...")

        res = self.session.get(url, timeout=10)
        if not res.ok:
            raise Exception(f"Failed to fetch page: {res.status_code}")

        # Extract dari React props
        match = re.search(r'({"props":{.*})', res.text)
        if not match:
            raise Exception("Could not find React props")

        data = orjson.loads(match.group(1))
        curVideoInfo = data['props']['initialState']['play']['curVideoInfo']

        self.video_info = {
            'title': curVideoInfo.get('name', 'Unknown'),
            'album': curVideoInfo.get('albumName', 'Unknown'),
            'duration': curVideoInfo.get('len', 0),
            'order': curVideoInfo.get('order', 0),
            'year': curVideoInfo.get('year', ''),
        }

        print(f"[✓] Video Info:")
        print(f"     Title: {self.video_info['title']}")
        print(f"     Album: {self.video_info['album']}")
        print(f"     Duration: {self.video_info['duration']} seconds")

        return self.video_info

    def capture_network_requests(self, url):
        """Buka browser dan capture network requests saat video diputar"""

        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not installed. Run: pip install playwright && python -m playwright install chromium")

        print("\n[2] Launching browser...")

        with sync_playwright() as p:
            # Launch browser (headless=False agar kita bisa lihat prosesnya)
            browser = p.chromium.launch(
                headless=False,  # Set ke True jika ingin background
                args=[
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )

            # Create context dengan cookies
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            )

            # Load cookies
            cookies = self._convert_cookies_to_playwright()
            if cookies:
                context.add_cookies(cookies)
                print(f"[✓] Loaded {len(cookies)} cookies")

            page = context.new_page()

            # Network monitoring
            def log_request(request):
                url = request.url
                resource_type = request.resource_type

                # Log video-related requests
                if any(ext in url for ext in ['.ts', '.m4s', '.mp4', '.m3u8', '.mpd']):
                    print(f"[📡] {resource_type}: {url[:100]}...")

                    if '.ts' in url or '.m4s' in url:
                        self.segment_urls.append(url)
                    elif any(ext in url for ext in ['.m3u8', '.mpd']):
                        self.manifest_urls.append(url)

            page.on('request', log_request)

            # Navigate to video page
            print(f"\n[3] Navigating to: {url}")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                print(f"[⚠️  Warning: Page load timeout (this is normal): {e}")
                print("[3] Continuing anyway...")

            # Wait untuk page loading
            import time
            print("[4] Waiting for player to load...")
            time.sleep(5)

            # Try to find dan click play button
            try:
                # Coba berbagai selector untuk play button
                play_selectors = [
                    'button[class*="play"]',
                    'button[aria-label*="play"]',
                    '[class*="play-button"]',
                    'div[class*="play"] >> button',
                    '.play-icon',
                    '#player-container button',
                ]

                play_clicked = False
                for selector in play_selectors:
                    try:
                        if page.is_visible(selector):
                            print(f"[5] Clicking play button: {selector}")
                            page.click(selector)
                            play_clicked = True
                            break
                    except:
                        continue

                if not play_clicked:
                    print("[5] Play button not found, trying to click video container...")
                    # Alternatif: click video container
                    page.click('video')
                    page.click('.player-controls')

            except Exception as e:
                print(f"[⚠️  Warning: Could not click play button: {e}")
                print("[5] Continuing anyway...")

            # Tunggu video bermain dan capture segment URLs
            print("\n[6] Capturing segment URLs...")
            print("     (Waiting 60 seconds for video to load and segments to appear...)")

            initial_count = len(self.segment_urls)
            last_count = initial_count

            # Extended wait time untuk capture lebih banyak segments
            for i in range(60):
                time.sleep(1)
                current_count = len(self.segment_urls)

                # Log progress jika ada segments baru
                if current_count > last_count:
                    print(f"     Found {current_count} segments (added {current_count - last_count})...")
                    last_count = current_count

                # Log setiap 5 seconds
                if i % 5 == 0 and current_count > 0:
                    print(f"     Progress: {i}/60 seconds - {current_count} segments captured")

            # Final count
            total_segments = len(self.segment_urls)
            total_manifests = len(self.manifest_urls)

            print(f"\n[✓] Capture complete!")
            print(f"     Segments found: {total_segments}")
            print(f"     Manifests found: {total_manifests}")

            # Simpan URLs untuk analisa
            capture_data = {
                'timestamp': datetime.now().isoformat(),
                'video_info': self.video_info,
                'segment_urls': self.segment_urls[:100],  # Save first 100
                'manifest_urls': self.manifest_urls,
                'total_segments': total_segments,
            }

            capture_file = self.output_dir / 'playwright_capture.json'
            with open(capture_file, 'w') as f:
                json.dump(capture_data, f, indent=2)

            print(f"[✓] Data saved to: {capture_file}")

            # Jangan close browser dulu, biarkan user lihat
            print("\n[INFO] Browser will stay open for 5 seconds...")
            print("       (You can watch the video being played)")
            time.sleep(5)

            browser.close()

            return capture_data

    def download_segments(self, max_segments=None):
        """Download semua segments yang sudah di-capture"""

        if not self.segment_urls:
            raise Exception("No segment URLs found! Run capture first.")

        # Filter dan deduplicate segments
        unique_segments = list(dict.fromkeys(self.segment_urls))  # Remove duplicates while keeping order

        if max_segments:
            unique_segments = unique_segments[:max_segments]

        print(f"\n[7] Downloading {len(unique_segments)} segments...")

        # Create folder untuk segments
        video_name = self._sanitize_filename(self.video_info.get('title', 'video'))
        segment_dir = self.output_dir / video_name / 'segments'
        segment_dir.mkdir(parents=True, exist_ok=True)

        # Download setiap segment
        downloaded = 0
        failed = 0

        for i, segment_url in enumerate(unique_segments):
            try:
                # Extract filename dari URL
                parsed = urlparse(segment_url)
                filename = os.path.basename(parsed.path)
                if not filename or len(filename) < 5:
                    filename = f"segment_{i:05d}.ts"

                output_path = segment_dir / filename

                # Check jika sudah ada
                if output_path.exists():
                    downloaded += 1
                    if (i + 1) % 10 == 0:
                        print(f"     Progress: {i+1}/{len(unique_segments)} (skipped existing)")
                    continue

                # Download
                response = self.session.get(segment_url, timeout=30, stream=True)

                if response.ok:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    downloaded += 1

                    if (i + 1) % 10 == 0 or downloaded == len(unique_segments):
                        percent = (downloaded / len(unique_segments) * 100)
                        print(f"     Progress: {downloaded}/{len(unique_segments)} ({percent:.1f}%)")
                else:
                    failed += 1
                    print(f"     [✗] Failed: {segment_url[:80]}...")

            except Exception as e:
                failed += 1
                print(f"     [✗] Error downloading segment {i}: {e}")

        print(f"\n[✓] Download complete!")
        print(f"     Successful: {downloaded}")
        print(f"     Failed: {failed}")
        print(f"     Saved to: {segment_dir}")

        return {
            'total': len(unique_segments),
            'downloaded': downloaded,
            'failed': failed,
            'segment_dir': str(segment_dir)
        }

    def merge_segments_with_ffmpeg(self, segment_dir):
        """Merge segments menjadi satu file video menggunakan ffmpeg"""

        import subprocess
        import glob

        print("\n[8] Merging segments with ffmpeg...")

        # Check ffmpeg
        try:
            subprocess.run(['ffmpeg', '-version'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         check=True)
        except:
            raise Exception("ffmpeg not found! Install with: brew install ffmpeg")

        segment_dir = Path(segment_dir)
        video_name = self._sanitize_filename(self.video_info.get('title', 'video'))

        # Create file list untuk ffmpeg
        segments = sorted(segment_dir.glob('*.ts'))

        if not segments:
            raise Exception(f"No segments found in {segment_dir}")

        print(f"     Found {len(segments)} segments")

        # Create concat list file
        concat_file = segment_dir / 'concat_list.txt'
        with open(concat_file, 'w') as f:
            for segment in segments:
                f.write(f"file '{segment.absolute()}'\n")

        # Output file
        output_file = self.output_dir / f"{video_name}.mp4"

        # Run ffmpeg
        print(f"     Merging to: {output_file}")
        print("     This may take a while...")

        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            str(output_file)
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        if result.returncode == 0:
            print(f"[✓] Merge complete: {output_file}")

            # Get file size
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"     File size: {size_mb:.2f} MB")

            return str(output_file)
        else:
            print(f"[✗] FFmpeg error:")
            print(result.stderr.decode())
            raise Exception("FFmpeg merge failed")

    def _sanitize_filename(self, name):
        """Sanitize filename untuk filesystem"""
        import re
        # Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.strip()
        return name if name else 'video'

    def download(self, url, merge_with_ffmpeg=True):
        """Complete download process"""

        try:
            # Step 1: Extract video info
            self.extract_video_info(url)

            # Step 2: Capture network requests dengan Playwright
            capture_data = self.capture_network_requests(url)

            if capture_data['total_segments'] == 0:
                print("\n[⚠️  Warning: No segments captured!")
                print("     This could mean:")
                print("     1. Video requires VIP/premium account")
                print("     2. Geo-blocking restriction")
                print("     3. Cookies expired")
                print("\n     Trying alternative method...")

                # Alternative: Try to get segments dari manifest
                return self._try_manifest_download(capture_data)

            # Step 3: Download segments
            download_result = self.download_segments()

            # Step 4: Merge dengan ffmpeg
            if merge_with_ffmpeg and download_result['downloaded'] > 0:
                output_file = self.merge_segments_with_ffmpeg(download_result['segment_dir'])

                print("\n" + "="*80)
                print("✓ DOWNLOAD COMPLETE!")
                print("="*80)
                print(f"Output: {output_file}")
                print(f"Segments: {download_result['downloaded']}/{download_result['total']}")
                print("="*80)

                return {
                    'success': True,
                    'output_file': str(output_file),
                    'segments_downloaded': download_result['downloaded'],
                    'video_info': self.video_info
                }

            return {
                'success': False,
                'message': 'No segments were downloaded'
            }

        except Exception as e:
            print(f"\n[✗] Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }

    def _try_manifest_download(self, capture_data):
        """Alternative method: Coba download dari manifest URLs"""
        print("\n[ALT] Trying alternative download method via manifest...")

        if not capture_data['manifest_urls']:
            print("[ALT] No manifest URLs found either")
            return {'success': False, 'message': 'No manifest URLs found'}

        # Coba download dari setiap manifest
        for manifest_url in capture_data['manifest_urls']:
            print(f"[ALT] Trying manifest: {manifest_url[:100]}...")

            try:
                res = self.session.get(manifest_url, timeout=15)
                if res.ok:
                    print(f"[ALT] Manifest type: {res.headers.get('content-type')}")

                    # Save manifest untuk analisa
                    manifest_type = 'm3u8' if '.m3u8' in manifest_url else 'mpd'
                    manifest_file = self.output_dir / f'manifest.{manifest_type}'
                    with open(manifest_file, 'w') as f:
                        f.write(res.text)

                    print(f"[ALT] Manifest saved: {manifest_file}")
                    print(f"[ALT] You can try using yt-dlp or ffmpeg with this manifest:")
                    print(f"      ffmpeg -i {manifest_file} -c copy video.mp4")

            except Exception as e:
                print(f"[ALT] Failed: {e}")

        return {
            'success': False,
            'message': 'Alternative method found manifests but could not auto-download. Check manifest files in output directory.'
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_iqiyi_video_playwright.py <iqiyi_play_url> [output_dir]")
        print("\nExample:")
        print("  python3 download_iqiyi_video_playwright.py https://www.iq.com/play/the-best-thing-episode-1-yy4gnywufo?lang=id_id")
        print("  python3 download_iqiyi_video_playwright.py https://www.iq.com/play/VIDEO_ID downloads")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'downloads'

    print("="*80)
    print("iQIYI Video Downloader - Playwright Edition")
    print("="*80)
    print(f"URL: {url}")
    print(f"Output: {output_dir}")
    print("="*80)

    downloader = IQIYIPlaywrightDownloader(output_dir=output_dir)
    result = downloader.download(url)

    if result.get('success'):
        print(f"\n✓ SUCCESS! Video saved to: {result['output_file']}")
        sys.exit(0)
    else:
        print(f"\n✗ FAILED: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
