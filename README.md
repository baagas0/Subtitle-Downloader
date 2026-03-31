# Subtitle Downloader

[![zh](https://img.shields.io/badge/lang-中文-blue)](https://github.com/wayneclub/Subtitle-Downloader/blob/main/README.zh-Hant.md) [![python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/)

**NON-COMMERCIAL USE ONLY**

Subtitle-Downloader supports downloading subtitles from multiple streaming services, such as Apple TV+, CatchPlay, Crunchyroll, Disney+, FridayVideo, HBO GO Asia, iQIYI, iTunes, KKTV, LINE TV, meWATCH, MyVideo, NowE, NowPlayer, Viki, Viu, WeTV, YouTube, etc.

## DESCRIPTION

Subtitle-Downloader is a command-line program to download subtitles from the most popular streaming platform. It requires **[Python 3.10+](https://www.python.org/downloads/)**, and **[NodeJS](https://nodejs.org/en/download)**. It should work on Linux, on Windows, or macOS. This project is only for personal research and language learning.

## INSTALLATION

- Linux, macOS:

```bash
pip install -r requirements.txt
```

- Windows: Execute `install_requirements.bat`

## Service Requirements

| Name | Authentication | Geo-blocking |
| ---- | -------------- | ------------ |
| Apple TV+ | Cookies | |
| CatchPlay | Cookies | Indonesia, Singapore, and Taiwan |
| Crunchyroll | Cookies | |
| Disney+ | Email & Password | |
| Friday Video | Cookies | Taiwan |
| HBO GO Asia | Email & Password | |
| iQIYI (iq.com) | Cookies | Partial region |
| iTunes | | |
| KKTV | | |
| LINE TV | | |
| MeWATCH | Profile Token | Singapore |
| MyVideo | Cookies | Taiwan |
| NowE | Cookies | |
| Now Player | Cookies | |
| Viki | Cookies | Partial region |
| Viu | | |
| WeTV | Cookies | Partial region |
| YouTube | Cookies (Subscribe channel) | |

### Get Cookies

1. Install Chrome plugin: [get-cookiestxt-locally](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Login to the streaming service, and use the plugin to download cookies.txt (Don't modify anything even the file name)
3. Put cookie.txt into `Subtitle-Downloader/cookies`

### Email & Password

- Fill your email and password in `Subtitle-Downloader/user_config.toml`

## USAGE

### Online **_(Colab environment is in the US, if you want to use it in another region please execute it locally)_**

1. Save a copy in Drive
2. Connect Colab
3. Install the requirements (Click 1st play button)
4. Depend the download platform and modify the text field  (Click the play button next to it when modified completely)
5. Download the subtitles from the left-side menu

<a href="https://colab.research.google.com/drive/1WdHOKNatft4J7DNOweP4gE2qtg7cvwEf?usp=sharing" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" title="Open this file in Google Colab" alt="Colab"/></a>

### Local

1. Depending on the download platform and modify `Subtitle-Downloader/user_config.toml`

    ```toml
    [subtitles]
    default-language = 'en'  # all/en/zh-Hant/zh-Hans/zh-HK/ja/ko
    default-format = '.srt'  # .srt/.ass
    archive = true           # true/false

    [headers]
    User-Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

    [credentials.DisneyPlus]
    email = ''
    password = ''

    [proxies]
    us = 'http:127.0.0.1:7890' # Clash

    [nordvpn]
    username = ''
    password = ''
    ```

2. Follow each platform's requirements and put cookies.txt into `Subtitle-Downloader/cookies`
3. Execute the program with the command line or `Subtitle-Downloader.bat` (Paste the title's URL)

    ```bash
    python subtitle_downloader.py URL [OPTIONS]
    ```

## OPTIONS

```text
  -h, --help                    show this help message and exit

  -s --season                   download season [0-9]

  -e --episode                  download episode [0-9]

  -l, --last-episode            download last episode

  -o, --output                  output directory

  -slang, --subtitle-language   languages of subtitles; use commas to separate multiple languages
                                default: Traditional Chinese
                                all: download all available languages

  -alang, --audio-language      languages of audio-tracks; use commas to separate multiple languages

  -sf, --subtitle-format        subtitles format: .srt or .ass

  -locale, --locale             interface language

  -p, --proxy                   proxy

  -d, --debug                   enable debug logging

  -v, --version                 app's version
```

## Subtitle Languages

Disney+

| Codec         | Language                           |
| ------------- | ---------------------------------- |
| en            | English [CC]                       |
| zh-Hant       | Chinese (Traditional)              |
| zh-Hans       | Chinese (Simplified)               |
| zh-HK         | Cantonese                          |
| da            | Dansk                              |
| de            | Deutsch                            |
| de-forced     | Deutsch [forced]                   |
| es-ES         | Español                            |
| es-ES-forced  | Español [forced]                   |
| es-419        | Español (Latinoamericano)          |
| es-419-forced | Español (Latinoamericano) [forced] |
| fr-FR         | Français                           |
| fr-FR-forced  | Français [forced]                  |
| fr-CA         | Français (Canadien)                |
| fr-CA-forced  | Français (Canadien) [forced]       |
| it            | Italiano                           |
| it-forced     | Italiano [forced]                  |
| ja            | Japanese                           |
| ja-forced     | Japanese [forced]                  |
| ko            | Korean                             |
| ko-forced     | Korean [forced]                    |
| nl            | Nederlands                         |
| no            | Norsk                              |
| pl            | Polski                             |
| pl-forced     | Polski [forced]                    |
| pt-PT         | Português                          |
| pt-BR         | Português (Brasil)                 |
| pt-BR-forced  | Português (Brasil) [forced]        |
| fi            | Suomi                              |
| sv            | Svenska                            |

HBO GO Asia

| Codec   | Language            |
| ------- | ------------------- |
| en      | English             |
| zh-Hant | Traditional Chinese |
| zh-Hans | Simplified Chinese  |
| ms      | Malay               |
| th      | Thai                |
| id      | Indonesian          |

iQIYI iq.com

| Codec   | Language            |
| ------- | ------------------- |
| en      | English             |
| zh-Hant | Traditional Chinese |
| zh-Hans | Simplified Chinese  |
| ms      | Malay               |
| vi      | Vietnamese          |
| th      | Thai                |
| id      | Indonesian          |
| es      | Spanish             |
| ko      | Korean              |
| ar      | Arabic              |

Viu
| Codec | Language |
| --- | --- |
| en | English |
| zh-Hant | Traditional Chinese |
| zh-Hans | Simplified Chinese |
| ms | Malay |
| th | Thai |
| id | Indonesian |
| my | Burmese |

WeTV
| Codec | Language |
| --- | --- |
| en | English |
| zh-Hant | Traditional Chinese |
| zh-Hans | Simplified Chinese |
| ms |
| th | Thai |
| id | Indonesian |
| pt | Português |
| es | Spanish |
| ko | Korean |

## iQIYI (iq.com) - Complete Guide

### Overview

iQIYI is one of the most complex services in this project due to its JavaScript-based authentication system. The implementation requires **NodeJS** to execute JavaScript code for generating encrypted parameters.

### Key Features

- **JavaScript Execution**: Requires NodeJS to run `cmd5x.js` for authentication
- **Complex DASH Authentication**: Uses multiple encrypted parameters including MD5 hashes
- **React Props Scraping**: Extracts video IDs from React initial state
- **Smart Geo-Fencing**: Auto-detects regions and sets proxy when needed
- **Multi-Format Support**: Handles both WebVTT and XML subtitle formats

### Prerequisites

#### 1. Python Dependencies
```bash
pip install -r requirements.txt
```

#### 2. NodeJS (REQUIRED)
iQIYI **requires NodeJS** to execute `services/iqiyi/cmd5x.js` for generating the `vf` parameter.

**Install NodeJS:**
- macOS: `brew install node`
- Linux: `sudo apt install nodejs npm`
- Windows: Download from [nodejs.org](https://nodejs.org/)

**Verify installation:**
```bash
node --version
```

### Authentication Setup

#### Method 1: Browser Extension (Recommended)

1. Install Chrome extension: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Login to [iq.com](https://www.iq.com/)
3. Click the extension → Export cookies → Select "iq.com"
4. Save as `www.iq.com_cookies.txt` in the `cookies/` folder

#### Method 2: Manual Extraction

1. Login to iq.com
2. Open DevTools (F12 or Cmd+Option+I)
3. Go to Application → Cookies → https://www.iq.com
4. Extract these required cookies:
   - `__dfp` (REQUIRED for authentication)
   - `P00003` (User ID)
   - `QC005` (Session ID)
5. Create `cookies/www.iq.com_cookies.txt` in Netscape cookie format

### Configuration

Edit `user_config.toml`:

```toml
[subtitles]
default-language = 'all'  # or en/zh-Hant/zh-Hans/ms/vi/th/id/es/ko/ar
default-format = '.srt'   # .srt/.ass/.vtt
archive = true            # true/false
fix-subtitle = true       # true/false

[credentials.iQIYI]
cookies = 'www.iq.com_cookies.txt'

# Proxy configuration for geo-blocking
[proxies]
sg = 'http://127.0.0.1:7890'  # Singapore
tw = 'http://127.0.0.1:7890'  # Taiwan
my = 'http://127.0.0.1:7890'  # Malaysia

# Or use NordVPN
[nordvpn]
username = 'your_service_credentials'
password = 'your_service_password'
```

### How It Works - Technical Deep Dive

The iQIYI subtitle extraction is a complex multi-step process that combines web scraping, JavaScript execution, and API calls. Here's the complete technical breakdown:

---

## Phase 1: Initial URL Processing & Metadata Extraction

### Step 1: URL Normalization (main() - Line 333-340)

**Function:** Convert play URL to album URL format

```python
# Input: https://www.iq.com/play/legend-of-fei-2021?lang=en_us
# Output: https://www.iq.com/album/legend-of-fei

if 'play/' in self.url:
    content_id = re.search(r'https://www.iq.com/play/.+\-([^-]+)\?lang=.+', self.url)
    if not content_id:
        content_id = re.search(r'https://www.iq.com/play/([^-]+)', self.url)
    self.url = f'https://www.iq.com/album/{content_id.group(1)}'
```

**Why:** Album URLs contain series metadata while play URLs are for individual videos. The system needs album-level data first.

---

### Step 2: Fetch Album Page & Extract React Props (main() - Line 342-355)

**API Used:** `GET {album_url}` (HTML page)

**Process:**
```python
# HTTP GET request to album page
res = self.session.get(url=self.url)

# Extract React initial state from HTML using regex
match = re.search(r'({"props":{.*})', res.text)

# Parse JSON with orjson (ultra-fast JSON parser)
data = orjson.loads(match.group(1))['props']
```

**What's Happening:**
- iQIYI uses React.js for frontend
- The entire initial state is embedded in HTML as JSON
- Regex extracts: `{"props":{"initialState":...,"initialProps":...}}`
- orjson is used instead of standard json for 2-3x faster parsing

**Data Extracted:**
```javascript
data['initialProps']['pageProps']['modeCode']  // e.g., "gt"
data['initialProps']['pageProps']['langCode']  // e.g., "en_us"
data['initialState']['album']['videoAlbumInfo'] = {
    "name": "Series Name",
    "albumId": "123456789",
    "videoType": "longVideo",  // or "singleVideo"
    "regionsAllowed": "sg,tw,my,hk",
    "from": 1,  // start episode
    "originalTotal": 40,  // total episodes
    "maxOrder": 40,  // current available episodes
    "year": "2021"
}
```

---

### Step 3: Geo-Fencing Check (main() - Line 357-364)

**API Used:** `GET https://ipapi.co/json/` (via utils/proxy.py)

```python
allow_regions = data['regionsAllowed'].split(',')
# ['sg', 'tw', 'my', 'hk']

# Check current IP location
current_country = get_ip_info()['country'].lower()

if current_country not in allow_regions:
    # Auto-set proxy to first allowed region
    self.set_proxy(allow_regions[0])
    # Verify proxy works
    if get_ip_info(self.session)['country'].lower() not in allow_regions:
        raise GeoBlockingError
```

**Example Flow:**
```
Current IP: Indonesia (id)
Allowed regions: ['sg', 'tw', 'my', 'hk']
→ Auto-set proxy to Singapore
→ Verify: Now IP shows Singapore
→ Continue
```

---

## Phase 2: Episode Discovery (Series Only)

### Step 4: Fetch Episode List with Pagination (series_subtitle() - Line 119-137)

**API Used:**
```
GET https://pcw-api.iq.com/api/v2/episodeListSource/{album_id}?platformId=3&modeCode={mode_code}&langCode={lang_code}&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder={end_order}&startOrder={start_order}
```

**Example URL:**
```
https://pcw-api.iq.com/api/v2/episodeListSource/123456789?platformId=3&modeCode=gt&langCode=en_us&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder=40&startOrder=1
```

**Pagination Logic:**
```python
# 24 episodes per page (iQIYI API limitation)
page_size = math.ceil(current_eps / 24)

# Page 1: episodes 1-24
# Page 2: episodes 25-40
for page in range(0, page_size):
    start_order = page * 24 + 1
    end_order = (page + 1) * 24
    if end_order > current_eps:
        end_order = current_eps

    # Build API URL
    episode_list_url = self.config['api']['episode_list'].format(
        album_id=album_id,
        mode_code=mode_code,
        lang_code=lang_code,
        end_order=current_eps,
        start_order=start_order
    )

    res = self.session.get(url=episode_list_url)
    episode_list += res.json()['data']['epg']
```

**API Response Structure:**
```json
{
  "code": "A00000",
  "data": {
    "epg": [
      {
        "qipuId": "987654321",
        "order": 1,
        "playLocSuffix": "legend-of-fei-2021-ep01",
        "episodeType": 0,
        "name": "Episode 1"
      },
      {
        "qipuId": "987654322",
        "order": 2,
        "playLocSuffix": "legend-of-fei-2021-ep02",
        "episodeType": 0,
        "name": "Episode 2"
      }
    ]
  }
}
```

**Episode Filtering:**
```python
# Skip trailers and specials (episodeType 1 or 6)
if episode['episodeType'] == 1 or episode['episodeType'] == 6:
    continue

# Filter by season/episode if user specified
if not self.download_season or season_index in self.download_season:
    if not self.download_episode or episode_index in self.download_episode:
        # Process this episode
```

---

## Phase 3: Video ID Extraction

### Step 5: Extract Video ID from Play URL (get_vid() - Line 36-57)

**API Used:** `GET https://www.iq.com/play/{playLocSuffix}` (HTML page)

**Process:**
```python
def get_vid(self, play_url):
    sleep(2)  # Rate limiting to avoid detection

    # Fetch play page HTML
    res = self.session.get(play_url, timeout=5)

    # Extract React props from HTML
    match = re.search(r'({"props":{.*})', res.text)

    # Parse JSON
    data = orjson.loads(match.group(1))

    # Navigate to video ID in React state
    vid = data['props']['initialState']['play']['curVideoInfo']['vid']

    return vid
```

**HTML Structure Scraped:**
```html
<!DOCTYPE html>
<html>
<head>
    <script>
        window.__INITIAL_STATE__ = {
            "props": {
                "initialState": {
                    "play": {
                        "curVideoInfo": {
                            "vid": "a1b2c3d4e5f6g7h8",  ← THIS IS WHAT WE NEED
                            "tvId": "987654321",
                            "name": "Episode 1",
                            ...
                        }
                    }
                }
            }
        }
    </script>
</head>
</html>
```

**Why This Method:**
- iQIYI doesn't provide video ID in episode list API
- Must scrape individual play page for each episode
- React state contains all video metadata
- Regex is faster and more reliable than full HTML parsing

**Rate Limiting:**
```python
sleep(2)  # 2-second delay between requests
```
Prevents IP blocking from iQIYI

---

## Phase 4: DASH URL Generation

### Step 6: Generate Authentication Key (get_auth_key() - Line 218-222)

```python
def get_auth_key(self, tvid):
    # Concatenate: MD5 SALT + timestamp + tvid
    text = f"d41d8cd98f00b204e9800998ecf8427e{int(time() * 1000)}{tvid}"

    # Create MD5 hash
    md = md5()
    md.update(text.encode())

    # Return hex digest
    return md.hexdigest()

# Example:
# Input: tvid = "987654321", timestamp = 1710000000000
# text = "d41d8cd98f00b204e9800998ecf8427e1710000000000987654321"
# Output: "3a7f8e9b2c1d4f5e6a8b9c0d1e2f3a4b"
```

**Components:**
- `d41d8cd98f00b204e9800998ecf8427e` - Static MD5 salt (empty string MD5)
- `int(time() * 1000)` - Current timestamp in milliseconds
- `tvid` - Video ID from episode list

---

### Step 7: Build DASH Parameters (get_dash_url() - Line 224-276)

**30+ Parameters Constructed:**

```python
params = {
    # Identifiers
    "tvid": tvid,                                    # Episode qipuId
    "vid": vid,                                      # Video ID from get_vid()
    "bid": "",                                       # Blank

    # Source indicators
    "src": "01011021010010000000",                   # Binary flags for source
    "vt": "0",                                       # Video type
    "rs": "1",                                       # Request source

    # User authentication from cookies
    "uid": self.cookies.get('P00003', '0'),         # User ID
    "k_uid": self.cookies['QC005'],                  # K UID
    "dfp": self.cookies['__dfp'],                    # Device fingerprint (REQUIRED)

    # Platform info
    "ori": "pcw",                                    # Origin: PC web
    "ps": "0",                                       # Platform status
    "pt": "0",                                       # Platform type
    "d": "0",                                        # Device
    "ut": "1",                                       # User type

    # Authentication
    "authKey": self.get_auth_key(tvid),              # MD5 hash
    "k_tag": "1",                                    # K tag

    # Timing
    "tm": int(time() * 1000),                        # Timestamp in ms

    # Feature flags (binary)
    "k_ft1": "143486267424900",                      # Feature set 1
    "k_ft4": "1581060",                              # Feature set 4
    "k_ft5": "1",                                    # Feature set 5
    "k_ft7": "4",                                    # Feature set 7

    # Other params
    "locale": "zh_cn",                               # Locale
    "prio": '{"ff":"","code":}',                     # Priority JSON
    "qdy": "a",                                      # QDY
    "qds": "0",                                      # QDS
    "bop": '{"version":"10.0","dfp":""}',           # BOP JSON
    "qd_v": "2",                                     # QD version
}
```

**Key Parameters Explained:**

| Parameter | Source | Purpose |
|-----------|--------|---------|
| `tvid` | Episode API | Episode identifier |
| `vid` | Play page scrape | Video stream identifier |
| `authKey` | Generated MD5 | Request authentication |
| `dfp` | Cookie `__dfp` | Device fingerprint (ANTI-BOT) |
| `uid` | Cookie `P00003` | User identification |
| `k_uid` | Cookie `QC005` | Session identification |
| `tm` | Current time | Request timestamp |

**Why So Many Parameters:**
- Anti-bot protection
- Device fingerprinting
- Request validation
- Analytics tracking
- DRM/Access control

---

### Step 8: Execute JavaScript for vf Parameter (get_dash_url() - Line 266-276)

**This is WHY NodeJS is Required!**

```python
# Build base URL without vf
url = "/dash?" + urlencode(params)

# Path to JavaScript file
cmdx5js = os.path.join(os.path.dirname(__file__), 'cmd5x.js')

# Execute JavaScript with NodeJS
executable = shutil.which('node')
process = subprocess.run(
    [executable, cmdx5js, url],
    stdout=subprocess.PIPE,
    check=False
)

# Capture vf parameter from JS output
vf = process.stdout.decode("utf-8").strip()

# Return complete DASH URL
return f"https://cache-video.iq.com{url}&vf={vf}"
```

**cmd5x.js Execution:**
```bash
node /path/to/cmd5x.js "/dash?tvid=987654321&vid=a1b2c3d4&..."

# Output: "e8f7a6b5c4d3e2f1a9b8c7d6e5f4a3b2c1d0e9f8"
```

**Why JavaScript:**
- iQIYI uses complex encryption algorithm
- `vf` parameter is result of custom encryption function
- Algorithm is too complex to port to Python
- Easier to execute original JS file

**cmd5x.js File:**
- Size: ~61KB
- Contains proprietary encryption algorithm
- Takes URL as argument
- Returns encrypted `vf` string

**Complete DASH URL Example:**
```
https://cache-video.iq.com/dash?tvid=987654321&vid=a1b2c3d4&src=01011021010010000000&...&vf=e8f7a6b5c4d3e2f1a9b8c7d6e5f4a3b2
```

---

## Phase 5: Subtitle Extraction

### Step 9: Fetch DASH Manifest (series_subtitle() - Line 188-213)

**API Used:** `GET {dash_url}` (Generated in Step 8)

```python
episode_res = self.session.get(url=dash_url)
episode_data = episode_res.json()['data']
```

**DASH API Response Structure:**
```json
{
  "code": "A00000",
  "data": {
    "program": {
      "stl": [  ← Subtitle array
        {
          "_name": "English",
          "webvtt": "\/\/meta.video.iqiyi.com\/subtitle\/a1b2c3d4.vtt",
          "lang": "en"
        },
        {
          "_name": "中文（繁體）",
          "xml": "\/\/meta.video.iqiyi.com\/subtitle\/e5f6g7h8.xml",
          "lang": "zh-Hant"
        },
        {
          "_name": "Bahasa Indonesia",
          "webvtt": "\/\/meta.video.iqiyi.com\/subtitle\/i9j0k1l2.vtt",
          "lang": "id"
        }
      ]
    }
  }
}
```

**Error Handling:**
```python
if 'boss_ts' in episode_data:
    # Geo-blocking or access denied
    self.logger.error(episode_data['boss_ts']['msg'])
elif 'program' not in episode_data:
    # Invalid vf parameter (cookies expired)
    self.logger.error("Invalid dash_url, wrong vf!")
    self.logger.error("Renew your cookies and try again!")
```

---

### Step 10: Parse Subtitle Metadata (get_subtitle() - Line 278-322)

```python
def get_subtitle(self, data, folder_path, filename):
    subtitles = []
    lang_paths = set()

    # Check if subtitles exist
    if 'stl' in data:
        available_languages = set()

        for sub in data['stl']:
            # Normalize language name to ISO 639-1 code
            sub_lang = get_language_code(sub['_name'])
            # "English" → "en"
            # "中文（繁體）" → "zh-Hant"
            # "Bahasa Indonesia" → "id"

            available_languages.add(sub_lang)

            # Check if user wants this language
            if sub_lang in self.subtitle_language or 'all' in self.subtitle_language:

                # Create language folder if multiple languages
                if len(self.subtitle_language) > 1 or 'all' in self.subtitle_language:
                    lang_folder_path = os.path.join(folder_path, sub_lang)
                else:
                    lang_folder_path = folder_path

                lang_paths.add(lang_folder_path)

                # Get subtitle link (prefer WebVTT over XML)
                if 'webvtt' in sub:
                    subtitle_link = sub['webvtt']
                    subtitle_filename = filename.replace('.vtt', f'.{sub_lang}.vtt')
                else:
                    subtitle_link = sub['xml']
                    subtitle_filename = filename.replace('.vtt', f'.{sub_lang}.xml')

                # Build complete URL
                subtitle_link = self.config['api']['meta'] + subtitle_link.replace('\\/', '/')
                # Result: https://meta.video.iqiyi.com/subtitle/a1b2c3d4.vtt

                # Create folder
                os.makedirs(lang_folder_path, exist_ok=True)

                # Build download metadata
                subtitle = {
                    'name': subtitle_filename,
                    'path': lang_folder_path,
                    'url': subtitle_link
                }
                subtitles.append(subtitle)

    return subtitles, lang_paths
```

**Subtitle URL Construction:**
```python
# Input from DASH: "\/\/meta.video.iqiyi.com\/subtitle\/a1b2c3d4.vtt"
# After replace: "//meta.video.iqiyi.com/subtitle/a1b2c3d4.vtt"
# With base: "https://meta.video.iqiyi.com/subtitle/a1b2c3d4.vtt"
```

---

### Step 11: Download Subtitle Files (download_subtitle() - Line 324-331)

```python
def download_subtitle(self, subtitles, languages, folder_path):
    if subtitles and languages:
        # Download all subtitle files (parallel downloads)
        download_files(subtitles)

        # Convert each language folder
        for lang_path in sorted(languages):
            convert_subtitle(
                folder_path=lang_path,
                subtitle_format=self.subtitle_format,
                locale=self.locale
            )

        # Convert main folder (merge all languages)
        convert_subtitle(
            folder_path=folder_path,
            platform=self.platform,
            subtitle_format=self.subtitle_format,
            locale=self.locale
        )
```

**Download Process (utils/io.py):**
- Parallel downloads using ThreadPoolExecutor
- Retry on failure (up to 3 times)
- Progress bar with tqdm
- Headers spoofing to avoid detection

**Conversion Process (utils/subtitle.py):**
```python
# Converts VTT/XML → SRT/ASS
# - Handles timecode conversion
# - Removes HTML tags
# - Fixes Chinese punctuation
# - Adds styling for ASS format
```

---

## Complete Flow Diagram

```
USER INPUT URL
    ↓
[1] Normalize URL (play → album)
    ↓
[2] Fetch Album Page HTML
    ├─ API: GET https://www.iq.com/album/{id}
    └─ Extract React props via regex
    ↓
[3] Parse Metadata
    ├─ modeCode, langCode
    ├─ videoAlbumInfo (title, episodes, regions)
    └─ Check videoType (series vs movie)
    ↓
[4] Geo-Fencing Check
    ├─ API: GET https://ipapi.co/json/
    ├─ Compare: currentIP vs allowedRegions
    └─ Auto-set proxy if needed
    ↓
[5] Fetch Episode List (Series Only)
    ├─ API: GET https://pcw-api.iq.com/api/v2/episodeListSource/...
    ├─ Pagination: 24 eps/page
    └─ Extract: qipuId, order, playLocSuffix
    ↓
[6] For Each Episode:
    ↓
    [6a] Fetch Play Page HTML
        ├─ API: GET https://www.iq.com/play/{playLocSuffix}
        ├─ Extract React props
        └─ Get: vid (video ID)
        ↓
    [6b] Generate DASH URL
        ├─ Build 30+ parameters (tvid, vid, authKey, cookies...)
        ├─ Execute cmd5x.js via NodeJS → vf parameter
        └─ Return: https://cache-video.iq.com/dash?...&vf=...
        ↓
    [6c] Fetch DASH Manifest
        ├─ API: GET {dash_url}
        └─ Parse: program.stl[] array
        ↓
    [6d] Extract Subtitle Metadata
        ├─ For each language in stl[]
        │   ├─ Normalize: "_name" → ISO 639-1 code
        │   ├─ Check: user wants this language?
        │   ├─ Get: webvtt or xml link
        │   ├─ Build: complete URL
        │   └─ Create: download metadata dict
        └─ Return: subtitles[], lang_paths[]
        ↓
    [6e] Download Subtitle Files
        ├─ Parallel download all URLs
        ├─ Save to: {folder}/{lang}/{filename}.vtt
        └─ Convert: VTT/XML → SRT/ASS
    ↓
[7] Organize Output
    └─ Structure: downloads/{Title.S01}/{lang}/{Title.S01E01.lang.srt}
```

---

## API Endpoints Summary

| Endpoint | Purpose | Method | Auth Required |
|----------|---------|--------|---------------|
| `https://www.iq.com/album/{id}` | Get series metadata | GET | None (public) |
| `https://www.iq.com/play/{id}` | Get video ID | GET | Cookies (__dfp, P00003, QC005) |
| `https://pcw-api.iq.com/api/v2/episodeListSource/{album_id}` | Get episode list | GET | None |
| `https://cache-video.iq.com/dash?...` | Get DASH manifest | GET | Cookies + vf parameter |
| `https://meta.video.iqiyi.com/subtitle/{id}.vtt` | Download subtitle | GET | Referer check |
| `https://ipapi.co/json/` | Get IP location | GET | None |

---

## Key Technical Challenges

### 1. React Props Scraping
**Challenge:** Dynamic data embedded in HTML
**Solution:** Regex + orjson for fast parsing

### 2. JavaScript Execution
**Challenge:** Python can't execute complex JS encryption
**Solution:** subprocess to NodeJS with cmd5x.js

### 3. Anti-Bot Protection
**Challenge:** 30+ parameters, device fingerprinting
**Solution:** Complete replication of browser request

### 4. Rate Limiting
**Challenge:** IP blocking from too many requests
**Solution:** 2-second delay between requests

### 5. Geo-Blocking
**Challenge:** Content restricted by region
**Solution:** Auto-detect + auto-set proxy

### 6. Cookie Management
**Challenge:** Cookies expire frequently
**Solution:** Clear error messages guide users to renew

### Key Functions (services/iqiyi/iqiyi.py)

#### `get_vid()` - Line 36
Extracts video ID from play URL by parsing React props embedded in HTML:
```python
res = self.session.get(play_url)
match = re.search(r'({"props":{.*})', res.text)
data = orjson.loads(match.group(1))
vid = data['props']['initialState']['play']['curVideoInfo']['vid']
```

#### `get_dash_url()` - Line 224
Generates DASH URL with encrypted parameters:
```python
# Build parameters
params = {
    "tvid": tvid,
    "vid": vid,
    "authKey": self.get_auth_key(tvid),  # MD5 hash
    "dfp": self.cookies['__dfp'],
    # ... many more parameters
}

# Execute cmd5x.js for 'vf' parameter
process = subprocess.run(['node', cmdx5js, url])
vf = process.stdout.decode("utf-8").strip()

return f"https://cache-video.iq.com{url}&vf={vf}"
```

**Why NodeJS?** iQIYI uses JavaScript-based encryption for the `vf` parameter that must be executed directly.

#### `get_subtitle()` - Line 278
Extracts subtitle metadata from DASH response:
```python
for sub in data['stl']:
    sub_lang = get_language_code(sub['_name'])
    if sub_lang in self.subtitle_language:
        # Get WebVTT or XML link
        subtitle_link = sub.get('webvtt', sub.get('xml'))
        # Build download metadata
        subtitle = {
            'name': filename,
            'path': lang_folder_path,
            'url': subtitle_link
        }
```

### Usage Examples

#### Basic Usage
```bash
# Download all episodes from a series
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx"

# Download season 1 episode 1
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -s 1 -e 1

# Download latest episode only
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -l
```

#### Advanced Options
```bash
# Download multiple episodes (1, 3, 5)
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -s 1 -e 1,3,5

# Download episode range (1-10)
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -s 1 -e 1-10

# Download with specific languages
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -slang en,zh-Hant,id

# Download all available languages
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -slang all

# Download with .ass format
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -sf .ass

# Download with proxy for geo-restricted content
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -p sg

# Debug mode for troubleshooting
python subtitle_downloader.py "https://www.iq.com/album/xxxxxx" -d
```

### API Endpoints (configs/iQIYI.toml)

```toml
[api]
# Get episode list for series
episode_list = 'https://pcw-api.iq.com/api/v2/episodeListSource/{album_id}?platformId=3&modeCode={mode_code}&langCode={lang_code}&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder={end_order}&startOrder={start_order}'

# Metadata server for subtitle files
meta = 'https://meta.video.iqiyi.com'
```

### Output Structure

#### Single Movie
```
downloads/
└── Movie Name.2024/
    ├── Movie.Name.2024.WEB-DL.iqiyi.en.srt
    ├── Movie.Name.2024.WEB-DL.iqiyi.zh-Hant.srt
    └── Movie.Name.2024.WEB-DL.iqiyi.id.srt
```

#### Series
```
downloads/
└── Series Name.S01/
    ├── Series.Name.S01E01.WEB-DL.iqiyi.en.srt
    ├── Series.Name.S01E01.WEB-DL.iqiyi.zh-Hant.srt
    ├── Series.Name.S01E02.WEB-DL.iqiyi.en.srt
    └── ...
```

#### Multiple Languages (separate folders)
```
downloads/
└── Series Name.S01/
    ├── en/
    │   ├── Series.Name.S01E01.WEB-DL.iqiyi.en.srt
    │   └── ...
    ├── zh-Hant/
    │   ├── Series.Name.S01E01.WEB-DL.iqiyi.zh-Hant.srt
    │   └── ...
    └── id/
        └── ...
```

### Troubleshooting

#### Error: "Nodejs not found"
**Solution:** Install NodeJS
```bash
# macOS
brew install node

# Linux
sudo apt install nodejs npm

# Windows
# Download from https://nodejs.org/
```

#### Error: "Can't find vid!"
**Causes:**
- Invalid play URL format
- Video not accessible in your region

**Solution:**
- Use album URL instead: `https://www.iq.com/album/xxxxxx`
- Check if video is playable in browser

#### Error: "Invaild dash_url, wrong vf!"
**Causes:**
- Cookies expired
- Invalid authentication parameters

**Solution:**
- Renew cookies from browser
- Clear cache and try again
- Verify `__dfp` cookie is present

#### Error: "This video is only allows in: sg, tw, my"
**Cause:** Geo-blocking restriction

**Solution:**
```bash
# Use proxy
python subtitle_downloader.py URL -p sg

# Or configure in user_config.toml
[proxies]
sg = 'http://127.0.0.1:7890'
```

#### No subtitles found
**Check:**
- Video has embedded subtitles (can be turned on/off)
- Video is playable in your region
- Try `-slang all` to see available languages
- Use `-d` flag for debug information

### Best Practices

1. **Always use album URLs** for series instead of play URLs
2. **Renew cookies regularly** - they expire after some time
3. **Use `-slang all`** to check all available languages
4. **Enable debug mode** (`-d`) for troubleshooting
5. **Configure proxy** for geo-restricted content
6. **Archive mode** creates ZIP files of downloaded subtitles

### Technical Details

- **Implementation File**: `services/iqiyi/iqiyi.py` (371 lines)
- **JS Encryption File**: `services/iqiyi/cmd5x.js` (~61KB)
- **Config File**: `configs/iQIYI.toml`
- **Authentication**: Cookies-based (`__dfp`, `P00003`, `QC005`)
- **Subtitle Formats**: WebVTT, XML (converted to .srt/.ass)
- **Pagination**: 24 episodes per page for series

### Recent Updates
- Commit `6c8f375`: update iq.com
- Commit `6b89ad6`: update iq.com

*Note: iQIYI API changes frequently, so the project is actively maintained to keep up with updates.*

## meWATCH

1. Login to [meWATCH](https://www.mewatch.sg/) on the browser.
2. Select a movie or series you want to download
3. Open the `devtools` in the browser (Windows: Ctrl + Shift + I or F12; macOS: ⌘ + ⌥ + I.)
4. Refresh the page and select `Network` on `devtools`
5. Type `https://www.mewatch.sg/api/account/profile` in the filter to find the profile api
6. Copy profile token (X-Authorization) from profile API Request Headers (Do not include `Bearer`, the profile token starts with `eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJ`) and paste in `Subtitle-Downloader/user_config.toml ([credentials.meWATCH] profile_token='')`.

## Now E, Now Player

- Copy the user-agent from login browser [https://www.whatsmyua.info/](https://www.whatsmyua.info/) and paste it in `Subtitle-Downloader/user_config.toml (User-Agent)`. The user-agent must be the same as login browser user-agent.

## More Examples

- Download all seasons and all episodes

```bash
python subtitle_downloader.py URL
```

- Download season 1 episode 1

```bash
python subtitle_downloader.py URL -s 1 -e 1
```

- Download season 1 episode 1's subtitle with all languages

```bash
python subtitle_downloader.py URL -s 1 -e 1 -slang all
```

- Download all episode subtitles in all languages: en, zh-Hant

```bash
python subtitle_downloader.py https://www.disneyplus.com/series/loki/6pARMvILBGzF -slang en,zh-Hant
```

- Download the latest episode

```bash
python subtitle_downloader.py URL -l
```

- Download season 1 episode 1-10

```bash
python subtitle_downloader.py URL -s 1 -e 1-10
```

- Download season 1 episode 1,3,5

```bash
python subtitle_downloader.py URL -s 1 -e 1,3,5
```

- Download season 1 episodes with NordVPN (region=tw)

```bash
python subtitle_downloader.py URL -s 1 -p tw
```

- Download season 1 episodes with proxy (Clash)

```bash
python subtitle_downloader.py URL -s 1 -p http:127.0.0.1:7890
```

- Download season 1 episodes with .ass format subtitle

```bash
python subtitle_downloader.py URL -s 1 -sf .ass
```

## NOTICE

- Few streaming services have Geo-blocking, make sure you are in the same region or use a proxy to bypass restrictions.
- Disney+ doesn't support VPN.
- Viki has API protection, don't call API too often. (Only catch 100% completed subtitles)

## FAQ

- Any issue during downloading subtitles, upload the screenshot and log file (Please provide title, platform, and region).
- Make sure the video contains embedded subtitles (subtitles able to turn on and off) and it is playable in your region.

## Support & Contributions

- Please ⭐️ this repository if this project helped you!
- Contributions of any kind are welcome!

 <a href="https://www.buymeacoffee.com/wayneclub" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/black_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

## Appendix

- Netflix: [Netflix subtitle downloader](https://greasyfork.org/en/scripts/26654-netflix-subtitle-downloader)
- Amazon (Prime Video): [Amazon subtitle downloader](https://greasyfork.org/en/scripts/34885-amazon-video-subtitle-downloader/feedback)
