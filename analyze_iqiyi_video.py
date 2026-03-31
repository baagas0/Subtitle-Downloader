#!/usr/bin/env python3
"""
Script untuk analisa bagaimana iQIYI menampilkan video
"""

import requests
import json
import subprocess
import os
from hashlib import md5
from time import time
from urllib.parse import urlencode
import http.cookiejar as cookiejar

# Load cookies
cookie_file = 'cookies/www.iq.com_cookies.txt'
cj = cookiejar.MozillaCookieJar(cookie_file)
cj.load(ignore_discard=True, ignore_expires=True)

# Create session dengan cookies
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Referer': 'https://www.iq.com/'
})

# Load cookies into session
for cookie in cj:
    session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)

def get_auth_key(tvid):
    text = f"d41d8cd98f00b204e9800998ecf8427e{int(time() * 1000)}{tvid}"
    md = md5()
    md.update(text.encode())
    return md.hexdigest()

def get_cookies_dict():
    return {
        '__dfp': session.cookies.get_dict().get('__dfp', ''),
        'P00003': session.cookies.get_dict().get('P00003', '0'),
        'QC005': session.cookies.get_dict().get('QC005', ''),
    }

# URL untuk analisa
play_url = "https://www.iq.com/play/the-best-thing-episode-1-yy4gnywufo?lang=id_id"

print("=" * 80)
print("STEP 1: Fetch Play Page untuk mendapatkan vid")
print("=" * 80)

res = session.get(play_url)
print(f"Status: {res.status_code}")

# Extract vid dari HTML
import re
import orjson

match = re.search(r'({"props":{.*})', res.text)
if match:
    data = orjson.loads(match.group(1))
    curVideoInfo = data['props']['initialState']['play']['curVideoInfo']
    vid = curVideoInfo['vid']
    # tvid mungkin di key berbeda, coba beberapa kemungkinan
    tvid = curVideoInfo.get('qipuId') or curVideoInfo.get('tvId') or curVideoInfo.get('tvid', '')

    print(f"\n✓ Video ID (vid): {vid}")
    print(f"✓ TV ID (tvid): {tvid}")
    print(f"\nAvailable keys in curVideoInfo: {list(curVideoInfo.keys())}")

    if not tvid:
        print("⚠ Warning: tvid not found, trying alternative method...")
        # Get from album data
        tvid = data['props']['initialState']['album']['videoAlbumInfo'].get('qipuId', '')
        print(f"✓ TV ID from album: {tvid}")
else:
    print("✗ Gagal extract vid")
    exit(1)

print("\n" + "=" * 80)
print("STEP 2: Generate DASH URL dengan vf parameter")
print("=" * 80)

cookies = get_cookies_dict()
print(f"\nCookies:")
print(f"  __dfp: {cookies['__dfp'][:20]}...")
print(f"  P00003: {cookies['P00003']}")
print(f"  QC005: {cookies['QC005'][:20]}...")

# Build parameters
params = {
    "tvid": tvid,
    "bid": "",
    "vid": vid,
    "src": "01011021010010000000",
    "vt": "0",
    "rs": "1",
    "uid": cookies['P00003'],
    "ori": "pcw",
    "ps": "0",
    "k_uid": cookies['QC005'],
    "pt": "0",
    "d": "0",
    "s": "",
    "lid": "",
    "slid": "0",
    "cf": "",
    "ct": "",
    "authKey": get_auth_key(tvid),
    "k_tag": "1",
    "ost": "0",
    "ppt": "0",
    "dfp": cookies['__dfp'],
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
print(f"\nBase URL (tanpa vf): {url[:100]}...")

# Execute cmd5x.js untuk dapat vf
cmdx5js = os.path.join(os.path.dirname(__file__), 'services/iqiyi/cmd5x.js')
print(f"\nExecuting cmd5x.js...")

executable = os.path.exists('/usr/local/bin/node') and '/usr/local/bin/node' or 'node'
process = subprocess.run(
    [executable, cmdx5js, url],
    stdout=subprocess.PIPE,
    check=False
)
vf = process.stdout.decode("utf-8").strip()
print(f"✓ vf parameter: {vf}")

dash_url = f"https://cache-video.iq.com{url}&vf={vf}"
print(f"\n✓ Complete DASH URL:")
print(f"  {dash_url[:150]}...")

print("\n" + "=" * 80)
print("STEP 3: Request DASH API")
print("=" * 80)

dash_res = session.get(dash_url)
print(f"\nStatus: {dash_res.status_code}")

if dash_res.ok:
    data = dash_res.json()

    # Save full response untuk analisa
    with open('dash_response.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("✓ Full response saved to dash_response.json")

    # Analisa structure
    print("\nResponse Structure:")
    print(f"  Keys: {list(data.keys())}")

    if 'data' in data:
        print(f"  data keys: {list(data['data'].keys())}")

        if 'program' in data['data']:
            program = data['data']['program']
            print(f"\n  Program keys: {list(program.keys())}")

            # Cek video streams
            if 'video' in program:
                print(f"\n  ✓ VIDEO DATA FOUND!")
                video = program['video']

                if isinstance(video, list):
                    print(f"    Video is array with {len(video)} items")
                    for i, v in enumerate(video[:3]):  # Show first 3
                        print(f"\n    Video {i+1}:")
                        for key in list(v.keys())[:10]:  # Show first 10 keys
                            val = v[key]
                            if isinstance(val, str) and len(val) > 100:
                                val = val[:100] + "..."
                            print(f"      {key}: {val}")
                elif isinstance(video, dict):
                    print(f"    Video is dict")
                    print(f"    Keys: {list(video.keys())}")

            # Cek audio streams
            if 'audio' in program:
                print(f"\n  ✓ AUDIO DATA FOUND!")
                audio = program['audio']
                if isinstance(audio, list):
                    print(f"    Audio is array with {len(audio)} items")
                    for i, a in enumerate(audio[:2]):
                        print(f"\n    Audio {i+1}:")
                        for key in list(a.keys())[:10]:
                            val = a[key]
                            if isinstance(val, str) and len(val) > 100:
                                val = val[:100] + "..."
                            print(f"      {key}: {val}")

            # Cek subtitle
            if 'stl' in program:
                print(f"\n  ✓ SUBTITLE DATA FOUND!")
                print(f"    Total subtitles: {len(program['stl'])}")

    print("\n" + "=" * 80)
    print("KEY FINDING: Video Stream URLs")
    print("=" * 80)

    # Cari URL video
    if 'data' in data and 'program' in data['data']:
        program = data['data']['program']

        # Method 1: Check 'video' key
        if 'video' in program:
            print("\nMethod 1: 'video' key")
            videos = program['video']
            if isinstance(videos, list) and len(videos) > 0:
                print(f"  Found {len(videos)} video streams")
                for i, vid_data in enumerate(videos[:2]):
                    print(f"\n  Video Stream {i+1}:")
                    print(f"    Keys: {list(vid_data.keys())}")

                    # Cari URL di berbagai kemungkinan key
                    for key in ['url', 'm3u8', 'dash_url', 'mp4_url', 'src']:
                        if key in vid_data:
                            print(f"    {key}: {vid_data[key][:200] if len(vid_data[key]) > 200 else vid_data[key]}")

        # Method 2: Check direct keys
        for key in ['m3u8', 'url', 'video_url', 'stream_url']:
            if key in program:
                print(f"\nMethod 2: '{key}' in program")
                print(f"  {program[key][:200] if len(str(program[key])) > 200 else program[key]}")

else:
    print(f"✗ Request failed: {dash_res.text}")
