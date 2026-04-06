# iQIYI Subtitle Downloader - Implementation Guide

## Table of Contents
1. [Setup and Configuration](#setup-and-configuration)
2. [Authentication Setup](#authentication-setup)
3. [Running the Downloader](#running-the-downloader)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Advanced Usage](#advanced-usage)
6. [Development and Extension](#development-and-extension)

## Setup and Configuration

### Prerequisites

**Required Software:**
1. **Python 3.7+**
   ```bash
   python --version
   ```

2. **Node.js** (for cmd5x.js execution)
   ```bash
   node --version
   ```

3. **Git** (for cloning repository)
   ```bash
   git --version
   ```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd subtitle-downloader
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Key dependencies:
   - `orjson` - Fast JSON parsing
   - `requests` - HTTP client
   - `pytomlpp` - TOML configuration parsing
   - `opencc` - Chinese text conversion
   - `cn2an` - Chinese number conversion

3. **Verify installation**
   ```bash
   python subtitle_downloader.py --help
   ```

### Configuration Files

#### 1. Main Configuration: `user_config.toml`

**Location:** Root directory

**Key Settings:**

```toml
# Language settings
locale = ''  # Empty = system locale, or 'en', 'zh-Hant', etc.

[subtitles]
default-language = 'all'  # all, en, zh-Hant, zh-Hans, zh-HK, ja, ko
default-format = '.srt'   # .srt, .ass, .vtt
archive = true            # Keep original files after conversion
fix-subtitle = true       # Apply subtitle fixes

[directories]
cookies = ''    # Empty = default 'cookies' directory
downloads = ''  # Empty = default 'downloads' directory

[headers]
User-Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

[credentials.iQIYI]
cookies = 'www.iq.com_cookies.txt'
```

#### 2. Service Configuration: `configs/iQIYI.toml`

**Location:** `configs/` directory

```toml
credentials = 'cookies'
required = '__dfp'

[api]
episode_list = 'https://pcw-api.iq.com/api/v2/episodeListSource/{album_id}?platformId=3&modeCode={mode_code}&langCode={lang_code}&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder={end_order}&startOrder={start_order}'
meta = 'https://meta.video.iqiyi.com'
```

**Do NOT modify these values** unless you understand the API structure.

## Authentication Setup

### Cookie-Based Authentication

iQIYI uses cookies for authentication. You must export cookies from your browser.

#### Step 1: Install Browser Extension

**Recommended:** "Get cookies.txt" extension
- Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbanldlwejp
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/get-cookiestxt-locally/

#### Step 2: Login to iQIYI

1. Visit https://www.iq.com in your browser
2. Login with your account
3. Ensure you can access premium content if needed

#### Step 3: Export Cookies

1. Click the browser extension icon
2. Select "Export" → "Download as cookies.txt"
3. Save the file

#### Step 4: Place Cookie File

**Option A: Use default location**
```bash
# Move to default cookies directory
mv ~/Downloads/www.iq.com_cookies.txt /path/to/subtitle-downloader/cookies/
```

**Option B: Use custom location**
```toml
# In user_config.toml
[directories]
cookies = '/path/to/your/cookies'

# Then update credentials
[credentials.iQIYI]
cookies = 'www.iq.com_cookies.txt'
```

#### Step 5: Verify Required Cookies

The cookie file must contain these cookies:

1. **`__dfp`** - Device fingerprint (REQUIRED)
2. **`QC005`** - Authentication key (REQUIRED)
3. **`P00003`** - User session (optional, defaults to '0')

**Check using:**
```bash
cat cookies/www.iq.com_cookies.txt | grep -E '__dfp|QC005|P00003'
```

**Example output:**
```
.iq.com	TRUE	/	FALSE	1735689600	__dfp	abc123def456...
.iq.com	TRUE	/	FALSE	1735689600	QC005	xyz789ghi012...
.iq.com	TRUE	/	FALSE	1735689600	P00003	user_token_here
```

### Common Authentication Issues

**Issue 1: Missing `__dfp` cookie**
```
Error: Missing "__dfp" in www.iq.com_cookies.txt
Solution:
1. Clear browser cache
2. Login again to iq.com
3. Wait 30 seconds for __dfp to be set
4. Export cookies again
```

**Issue 2: Expired cookies**
```
Error: vf validation failed
Solution:
1. Cookies expire after some time
2. Re-export cookies from browser
3. Replace old cookie file
```

**Issue 3: Region restriction**
```
Error: This video is only allows in: tw, hk, my
Solution:
1. Use proxy from allowed region
2. Configure in user_config.toml:
   [proxies]
   tw = 'http://proxy-server:port'
```

## Running the Downloader

### Basic Usage

#### Download Movie Subtitles

```bash
python subtitle_downloader.py --service iqiyi "https://www.iq.com/play/movie-abc123?lang=zh_tw"
```

**Output:**
```
downloads/
  Movie.Name.2023/
    Movie.Name.2023.zh_cn.srt
    Movie.Name.2023.en.srt
```

#### Download Series Subtitles (All Episodes)

```bash
python subtitle_downloader.py --service iqiyi "https://www.iq.com/album/series-abc123"
```

**Output:**
```
downloads/
  Series.Name.S01/
    Series.Name.S01E01.zh_cn.srt
    Series.Name.S01E01.en.srt
    Series.Name.S01E02.zh_cn.srt
    Series.Name.S01E02.en.srt
    ...
```

### Advanced Options

#### Filter by Season

```bash
# Download only Season 2
python subtitle_downloader.py --service iqiyi \
  --season 2 \
  "https://www.iq.com/album/series-abc123"
```

#### Filter by Episode

```bash
# Download only episodes 1, 3, 5
python subtitle_downloader.py --service iqiyi \
  --episode 1,3,5 \
  "https://www.iq.com/album/series-abc123"
```

#### Combine Season and Episode

```bash
# Download Season 1, episodes 1-5
python subtitle_downloader.py --service iqiyi \
  --season 1 \
  --episode 1,2,3,4,5 \
  "https://www.iq.com/album/series-abc123"
```

#### Language Selection

```bash
# Download only Chinese subtitles
python subtitle_downloader.py --service iqiyi \
  --subtitle-language zh-Hans \
  "https://www.iq.com/play/movie-abc123"

# Download multiple specific languages
python subtitle_downloader.py --service iqiyi \
  --subtitle-language zh-Hans,en \
  "https://www.iq.com/play/movie-abc123"

# Download all available languages
python subtitle_downloader.py --service iqiyi \
  --subtitle-language all \
  "https://www.iq.com/play/movie-abc123"
```

#### Output Format

```bash
# Convert to SRT (default)
python subtitle_downloader.py --service iqiyi \
  --subtitle-format .srt \
  "https://www.iq.com/play/movie-abc123"

# Convert to ASS
python subtitle_downloader.py --service iqiyi \
  --subtitle-format .ass \
  "https://www.iq.com/play/movie-abc123"

# Keep original VTT format
python subtitle_downloader.py --service iqiyi \
  --subtitle-format .vtt \
  "https://www.iq.com/play/movie-abc123"
```

#### Custom Output Directory

```bash
python subtitle_downloader.py --service iqiyi \
  --output /path/to/output \
  "https://www.iq.com/play/movie-abc123"
```

#### Download Last Episode Only

```bash
python subtitle_downloader.py --service iqiyi \
  --last-episode \
  "https://www.iq.com/album/series-abc123"
```

#### Use Proxy

```bash
# Use specific proxy server
python subtitle_downloader.py --service iqiyi \
  --proxy http://proxy-server:port \
  "https://www.iq.com/play/movie-abc123"

# Use proxy for specific country (from config)
python subtitle_downloader.py --service iqiyi \
  --proxy tw \
  "https://www.iq.com/play/movie-abc123"
```

### Complete Command Example

```bash
python subtitle_downloader.py \
  --service iqiyi \
  --season 1 \
  --episode 1,2,3 \
  --subtitle-language zh-Hans,en,ja \
  --subtitle-format .srt \
  --output /Users/user/Subtitles \
  "https://www.iq.com/series/drama-abc123"
```

## Troubleshooting Guide

### Common Errors and Solutions

#### Error 1: "Nodejs not found"

**Error Message:**
```
EnvironmentError: Nodejs not found...
```

**Solution:**
```bash
# Install Node.js
# macOS
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm

# Windows
# Download from https://nodejs.org/

# Verify installation
node --version
```

#### Error 2: "Please input correct play url!"

**Error Message:**
```
ERROR: Please input correct play url!
```

**Causes:**
1. Invalid URL format
2. URL doesn't contain video
3. Region-restricted content

**Solution:**
```bash
# Verify URL format
# Correct:
https://www.iq.com/play/abc123-def456?lang=zh_tw
https://www.iq.com/album/abc123

# Incorrect:
https://www.iq.com/
https://www.iq.com/search/...

# Check if content is accessible in browser
```

#### Error 3: "vf validation failed"

**Error Message:**
```
ERROR: Invalid dash_url, wrong vf!
ERROR: Renew your cookies and try again!
```

**Causes:**
1. Expired cookies
2. Missing required cookies
3. Invalid vf parameter generation

**Solution:**
```bash
# 1. Re-export cookies from browser
# 2. Verify all required cookies present
cat cookies/www.iq.com_cookies.txt | grep -E '__dfp|QC005|P00003'

# 3. Replace cookie file
mv ~/Downloads/www.iq.com_cookies.txt cookies/

# 4. Try again
```

#### Error 4: "Can't find vid!"

**Error Message:**
```
ERROR: Can't find vid!
```

**Causes:**
1. Video not available
2. Invalid play URL
3. Region restriction

**Solution:**
```bash
# 1. Verify video plays in browser
# 2. Check URL is correct
# 3. Try using proxy
python subtitle_downloader.py --service iqiyi --proxy tw "URL"
```

#### Error 5: "This video is only allows in: ..."

**Error Message:**
```
ERROR: This video is only allows in: tw, hk, my
```

**Solution:**
```bash
# Option 1: Use proxy from allowed region
python subtitle_downloader.py --service iqiyi --proxy tw "URL"

# Option 2: Configure proxy in user_config.toml
[proxies]
tw = 'http://proxy-server:port'

# Option 3: Use NordVPN (if configured)
python subtitle_downloader.py --service iqiyi --proxy tw "URL"
```

#### Error 6: "Sorry, there's no embedded subtitles in this video!"

**Error Message:**
```
ERROR: Sorry, there's no embedded subtitles in this video!
```

**Causes:**
1. Video doesn't have subtitles
2. Subtitles not loaded yet

**Solution:**
```bash
# 1. Verify subtitles exist in browser
# 2. Try different language option
python subtitle_downloader.py --service iqiyi --subtitle-language all "URL"

# 3. Some videos may not have subtitles at all
```

#### Error 7: Slow Download / Timeout

**Error Message:**
```
ERROR: timeout
```

**Solution:**
```bash
# 1. Check internet connection
ping www.iq.com

# 2. Use proxy
python subtitle_downloader.py --service iqiyi --proxy http://fast-proxy:port "URL"

# 3. Increase timeout (modify code in iqiyi.py)
# Change timeout=5 to timeout=30 in get() calls
```

### Debug Mode

Enable debug logging to see detailed API calls:

```bash
# Method 1: Use --log-level flag
python subtitle_downloader.py --service iqiyi \
  --log-level DEBUG \
  "https://www.iq.com/play/movie-abc123"

# Method 2: Modify user_config.toml
[logging]
level = "DEBUG"
```

**Debug Output Shows:**
- All API URLs called
- Request parameters
- Response data (truncated)
- File paths
- Error details

## Advanced Usage

### Batch Processing

Download multiple movies/series in sequence:

```bash
#!/bin/bash
# download_batch.sh

URLS=(
  "https://www.iq.com/play/movie1"
  "https://www.iq.com/play/movie2"
  "https://www.iq.com/album/series1"
)

for url in "${URLS[@]}"; do
  echo "Downloading: $url"
  python subtitle_downloader.py --service iqiyi "$url"
  echo "Waiting 10 seconds..."
  sleep 10
done
```

Run:
```bash
chmod +x download_batch.sh
./download_batch.sh
```

### Integration with Other Tools

#### 1. Combine with Video Downloaders

```bash
# Download video with yt-dlp
yt-dlp -f best "https://www.iq.com/play/movie-abc123"

# Download subtitles
python subtitle_downloader.py --service iqiyi "https://www.iq.com/play/movie-abc123"

# Organize files
mv movie_video.mp4 downloads/Movie.Name.2023/
```

#### 2. Automated Monitoring

```python
# monitor_new_episodes.py
import time
from subtitle_downloader import main

def check_for_new_episodes(album_url):
    # Check if new episodes available
    # If yes, download subtitles
    main(['--service', 'iqiyi', album_url])

# Check daily
while True:
    check_for_new_episodes("https://www.iq.com/album/series-abc123")
    time.sleep(86400)  # 24 hours
```

### Custom Language Mapping

Create custom language mappings in `utils/helper.py`:

```python
# Add to get_language_code() function
LANGUAGE_MAP = {
    '简体中文': 'zh_cn',
    '繁體中文': 'zh_tw',
    'Your Custom Language': 'custom_lang',
    # ...
}
```

### Subtitle Post-Processing

Create custom conversion scripts:

```python
# post_process.py
import os
import chardet

def fix_encoding(folder_path):
    """Fix subtitle encoding issues"""
    for file in os.listdir(folder_path):
        if file.endswith('.srt'):
            file_path = os.path.join(folder_path, file)

            # Detect encoding
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())

            # Convert to UTF-8
            if result['encoding'] != 'utf-8':
                with open(file_path, 'r', encoding=result['encoding']) as f:
                    content = f.read()

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

# Usage
fix_encoding('downloads/Movie.Name.2023')
```

## Development and Extension

### Understanding the Code Structure

```
subtitle-downloader/
├── services/
│   ├── baseservice.py          # Base class with common functionality
│   └── iqiyi/
│       ├── iqiyi.py           # Main IQIYI service implementation
│       └── cmd5x.js           # VF parameter generation (Node.js)
├── utils/
│   ├── helper.py              # Helper functions
│   ├── io.py                  # File I/O operations
│   ├── subtitle.py            # Subtitle conversion
│   └── proxy.py               # Proxy management
├── configs/
│   └── iQIYI.toml            # IQIYI-specific configuration
├── user_config.toml          # Main user configuration
└── subtitle_downloader.py    # Entry point
```

### Adding New Features

#### Feature: Download Multiple Languages Simultaneously

Current implementation already supports this. Use:
```bash
--subtitle-language all
```

#### Feature: Add Progress Callback

Modify `utils/io.py`:
```python
def download_files(subtitles, callback=None):
    """Download subtitle files with progress callback"""
    for i, subtitle in enumerate(subtitles):
        # Download logic
        if callback:
            callback(i, len(subtitles), subtitle['name'])
```

#### Feature: Export Download History

Add to `iqiyi.py`:
```python
import csv
from datetime import datetime

def log_download(self, title, url, languages):
    """Log download to CSV file"""
    log_file = 'download_history.csv'
    file_exists = os.path.isfile(log_file)

    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Title', 'URL', 'Languages'])

        writer.writerow([
            datetime.now().isoformat(),
            title,
            url,
            ','.join(languages)
        ])
```

### Testing

#### Test Authentication

```python
# test_auth.py
from services.iqiyi import IQIYI
import argparse

parser = argparse.ArgumentParser()
args = parser.parse_args()

# Setup args manually
args.url = "https://www.iq.com/play/test-video"
args.service = {'name': 'iQIYI'}
args.locale = 'en'
args.config = None
args.output = None
args.season = None
args.episode = None
args.last_episode = False
args.proxy = None
args.subtitle_language = 'all'
args.subtitle_format = '.srt'
args.log = ...  # Setup logger

iqiyi = IQIYI(args)
print("Cookies loaded:", '__dfp' in iqiyi.cookies)
print("Can access API:", len(iqiyi.session.get('https://www.iq.com').text) > 0)
```

#### Test API Calls

```python
# test_api.py
import requests

cookies = {
    '__dfp': 'your_dfp_value',
    'QC005': 'your_qc005_value',
    'P00003': 'your_p00003_value'
}

# Test album page
response = requests.get('https://www.iq.com/album/test', cookies=cookies)
print("Album page status:", response.status_code)

# Test episode list API
response = requests.get(
    'https://pcw-api.iq.com/api/v2/episodeListSource/test?platformId=3...',
    cookies=cookies
)
print("Episode list status:", response.status_code)
```

### Performance Optimization

#### 1. Parallel Episode Processing

Current implementation processes episodes sequentially. To parallelize:

```python
from concurrent.futures import ThreadPoolExecutor

def process_episode(episode, iqiyi_instance):
    """Process single episode"""
    return iqiyi_instance.get_subtitle(...)

# In series_subtitle()
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for episode in episode_list:
        future = executor.submit(process_episode, episode, self)
        futures.append(future)

    for future in futures:
        subs, lang_paths = future.result()
        subtitles += subs
        languages.update(lang_paths)
```

#### 2. Caching

Cache frequently accessed data:

```python
import pickle
import os
from datetime import timedelta

class Cache:
    def __init__(self, cache_file='.iqiyi_cache.pkl', max_age=timedelta(hours=1)):
        self.cache_file = cache_file
        self.max_age = max_age
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        return {}

    def get(self, key):
        if key in self.cache:
            timestamp, value = self.cache[key]
            if datetime.now() - timestamp < self.max_age:
                return value
        return None

    def set(self, key, value):
        self.cache[key] = (datetime.now(), value)
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

# Use in get_vid()
cache = Cache()
cached_vid = cache.get(play_url)
if cached_vid:
    return cached_vid

vid = extract_vid_from_page(play_url)
cache.set(play_url, vid)
return vid
```

### Contributing

When extending functionality:

1. **Maintain compatibility** with existing code
2. **Add error handling** for new features
3. **Update documentation** with new options
4. **Test thoroughly** with various content types
5. **Follow code style** (PEP 8 for Python)

## Best Practices

1. **Always check cookies before downloading**
   ```bash
   cat cookies/www.iq.com_cookies.txt | grep __dfp
   ```

2. **Use debug mode when troubleshooting**
   ```bash
   --log-level DEBUG
   ```

3. **Respect rate limiting**
   - Built-in 2-second delay between vid requests
   - Don't remove these delays

4. **Keep cookies updated**
   - Re-export weekly
   - Update after authentication errors

5. **Monitor for API changes**
   - iQIYI may change API endpoints
   - Update `configs/iQIYI.toml` if needed

6. **Use appropriate output formats**
   - .srt for most players
   - .ass for styling support
   - .vtt for web players

## Summary

This implementation guide covers:
- Complete setup and configuration
- Authentication setup with detailed troubleshooting
- Command-line usage with all options
- Comprehensive troubleshooting for common errors
- Advanced usage patterns and batch processing
- Development guidelines for extending functionality

For detailed API and data flow information, refer to:
- `IQIYI-ARCHITECTURE.md` - System architecture
- `IQIYI-API-REFERENCE.md` - Complete API documentation
- `IQIYI-DATA-FLOW.md` - Detailed data flow and logging
