#!/usr/bin/env python3
"""
Analisa iQIYI video loading dengan Playwright
"""

from playwright.sync_api import sync_playwright
import json
import time

def main():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set False untuk melihat browser
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        # Load cookies
        print("Loading cookies...")
        try:
            with open('cookies/www.iq.com_cookies.txt', 'r') as f:
                cookies_txt = f.read()
                # Parse Netscape cookie format (simplified)
                for line in cookies_txt.split('\n'):
                    if not line.startswith('#') and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 7:
                            context.add_cookies([{
                                'name': parts[5],
                                'value': parts[6],
                                'domain': parts[0],
                                'path': parts[2],
                            }])
        except Exception as e:
            print(f"Warning: Could not load cookies: {e}")

        page = context.new_page()

        # Capture network requests
        video_urls = []
        manifest_urls = []
        segment_urls = []

        def log_request(request):
            url = request.url
            # Log video-related requests
            if any(ext in url for ext in ['.m3u8', '.mpd', '.xml', '.ts', '.m4s', '.mp4']):
                resource_type = request.resource_type
                print(f"[REQUEST] {resource_type}: {url[:100]}")

                if '.m3u8' in url:
                    manifest_urls.append(url)
                elif '.mpd' in url or '.xml' in url:
                    manifest_urls.append(url)
                elif any(ext in url for ext in ['.ts', '.m4s']):
                    segment_urls.append(url)
                elif '.mp4' in url:
                    video_urls.append(url)

        page.on('request', log_request)

        # Navigate to video page
        url = "https://www.iq.com/play/the-best-thing-episode-1-yy4gnywufo?lang=id_id"
        print(f"\nNavigating to: {url}")
        page.goto(url, wait_until='networkidle', timeout=60000)

        print("\nWaiting for video player to load...")
        time.sleep(5)

        # Try to find and click play button
        try:
            play_button = page.locator('[class*="play"], [class*="Play"], button[aria-label*="play"]').first
            if play_button.is_visible():
                print("Clicking play button...")
                play_button.click()
                time.sleep(10)  # Wait for video to start playing and segments to load
        except:
            print("Could not find play button, waiting anyway...")
            time.sleep(10)

        print("\n" + "="*80)
        print("CAPTURED URLS")
        print("="*80)

        print(f"\nManifest URLs (M3U8/MPD/XML): {len(manifest_urls)}")
        for i, url in enumerate(manifest_urls):
            print(f"  {i+1}. {url}")

        print(f"\nVideo Segment URLs: {len(segment_urls)}")
        if segment_urls:
            for i, url in enumerate(segment_urls[:10]):  # Show first 10
                print(f"  {i+1}. {url[:120]}...")

        print(f"\nDirect Video URLs: {len(video_urls)}")
        for i, url in enumerate(video_urls):
            print(f"  {i+1}. {url}")

        # Save results
        results = {
            'manifest_urls': manifest_urls,
            'segment_urls': segment_urls[:50],  # Save first 50
            'video_urls': video_urls,
        }

        with open('playwright_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to playwright_analysis.json")

        # Keep browser open for inspection
        print("\nPress Enter to close browser...")
        input()

        browser.close()

if __name__ == '__main__':
    main()
