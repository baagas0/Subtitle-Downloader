# iQIYI API Reference - Complete Documentation

## Table of Contents
1. [API Endpoints Overview](#api-endpoints-overview)
2. [Authentication Mechanism](#authentication-mechanism)
3. [API Endpoints Detail](#api-endpoints-detail)
4. [Data Structures](#data-structures)
5. [Request/Response Examples](#requestresponse-examples)

## API Endpoints Overview

### Primary APIs Used

| API | Purpose | Method | Authentication |
|-----|---------|--------|----------------|
| Album Page | Get album/metadata | GET | Cookies |
| Episode List | Get episode list for series | GET | Cookies |
| Play Page | Extract video ID (vid) | GET | Cookies |
| DASH API | Get subtitle metadata | GET | Cookies + Custom Auth |
| Subtitle Download | Download subtitle files | GET | Direct URLs |

### Base Domains
- **Main domain:** `https://www.iq.com`
- **API domain:** `https://pcw-api.iq.com`
- **Video cache:** `https://cache-video.iq.com`
- **Metadata:** `https://meta.video.iqiyi.com`

## Authentication Mechanism

### Cookie-Based Authentication

The service uses cookies for authentication. Required cookies:

1. **`__dfp`** - Device fingerprint (REQUIRED)
   - Used for device identification
   - Required by config validation

2. **`P00003`** - User authentication token
   - User session identifier
   - Optional (defaults to '0' if missing)

3. **`QC005`** - Additional authentication
   - Used as k_uid parameter
   - Required for DASH requests

### Dynamic Auth Key Generation

**Location:** `get_auth_key(self, tvid)` - Line 218-222

```python
def get_auth_key(self, tvid):
    text = f"d41d8cd98f00b204e9800998ecf8427e{int(time() * 1000)}{tvid}"
    md = md5()
    md.update(text.encode())
    return md.hexdigest()
```

**Components:**
- Static salt: `d41d8cd98f00b204e9800998ecf8427e` (MD5 of empty string)
- Current timestamp: `int(time() * 1000)` (milliseconds)
- TV ID: The video's qipuId

**Example:**
```
Input: tvid = "1234567890", timestamp = 1699776000000
Text: "d41d8cd98f00b204e9800998ecf8427e16997760000001234567890"
Output: "a1b2c3d4e5f6..." (32-character MD5 hex)
```

### VF Parameter Generation

**Location:** `get_dash_url()` - Line 224-276

The `vf` parameter is generated using Node.js to execute `cmd5x.js`:

```python
url = "/dash?" + urlencode(params)
cmdx5js = os.path.join(os.path.dirname(__file__).replace('\\', '/'), 'cmd5x.js')
process = subprocess.run(
    [executable, cmdx5js, url],
    stdout=subprocess.PIPE,
    check=False
)
vf = process.stdout.decode("utf-8").strip()
```

The `vf` parameter is a critical validation parameter computed from all DASH URL parameters.

## API Endpoints Detail

### 1. Album/Playlist Page

**Purpose:** Get initial content metadata and determine content type

**URL Format:** `https://www.iq.com/album/{album_id}`

**Example:** `https://www.iq.com/album/abc123def456`

**Request:**
```python
res = self.session.get(url=self.url)
```

**Response (HTML with embedded JSON):**
```html
<script>
  self.__state = {"props":{"initialState":{...}, "initialProps":{...}}}
</script>
```

**Extraction Method:**
```python
match = re.search(r'({\"props\":{.*})', res.text)
data = orjson.loads(match.group(1))['props']
```

**Key Data Extracted:**
```json
{
  "initialProps": {
    "pageProps": {
      "modeCode": "crystal",
      "langCode": "zh_tw"
    }
  },
  "initialState": {
    "album": {
      "videoAlbumInfo": {
        "name": "Series Name",
        "albumId": "abc123",
        "year": "2023",
        "videoType": "singleVideo|longVideo",
        "regionsAllowed": "tw,hk,my",
        "from": 1,
        "originalTotal": 20,
        "maxOrder": 20
      }
    }
  }
}
```

**Fields:**
- `modeCode`: Content mode identifier
- `langCode`: Language code
- `name`: Content title
- `albumId`: Unique album identifier
- `year`: Release year
- `videoType`: "singleVideo" (movie) or other (series)
- `regionsAllowed`: Comma-separated country codes
- `from`: Starting episode number
- `originalTotal`: Total episodes in series
- `maxOrder`: Current available episodes

---

### 2. Episode List API

**Purpose:** Get list of episodes for series content

**URL Format:**
```
https://pcw-api.iq.com/api/v2/episodeListSource/{album_id}?platformId=3&modeCode={mode_code}&langCode={lang_code}&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder={end_order}&startOrder={start_order}
```

**Example:**
```
https://pcw-api.iq.com/api/v2/episodeListSource/abc123?platformId=3&modeCode=crystal&langCode=zh_tw&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder=24&startOrder=1
```

**Request:**
```python
episode_list_url = self.config['api']['episode_list'].format(
    album_id=album_id,
    mode_code=mode_code,
    lang_code=lang_code,
    end_order=current_eps,
    start_order=start_order
)
res = self.session.get(url=episode_list_url, timeout=5)
```

**Response:**
```json
{
  "code": "A00000",
  "data": {
    "epg": [
      {
        "qipuId": "1234567890",
        "order": 1,
        "playLocSuffix": "abc123-1234567890?lang=zh_tw",
        "episodeType": 0,
        "name": "Episode 1 Title"
      },
      {
        "qipuId": "1234567891",
        "order": 2,
        "playLocSuffix": "abc123-1234567891?lang=zh_tw",
        "episodeType": 0,
        "name": "Episode 2 Title"
      }
    ]
  }
}
```

**Fields:**
- `qipuId`: Unique episode identifier (tvid)
- `order`: Episode number
- `playLocSuffix`: URL suffix for play page
- `episodeType`: Episode type filter (0=normal, 1/6=skip)
- `name`: Episode title

**Pagination:**
- Page size: 24 episodes per request
- Calculation: `math.ceil(current_eps / 24)`

---

### 3. Play Page (Video ID Extraction)

**Purpose:** Extract video ID (vid) needed for DASH API

**URL Format:** `https://www.iq.com/play/{playLocSuffix}`

**Example:** `https://www.iq.com/play/abc123-1234567890?lang=zh_tw`

**Request:**
```python
sleep(2)  # Rate limiting
res = self.session.get(play_url, timeout=5)
```

**Response (HTML with embedded JSON):**
```html
<script>
  self.__state = {"props":{"initialState":{...}}}
</script>
```

**Extraction:**
```python
match = re.search(r'({\"props\":{.*})', res.text)
data = orjson.loads(match.group(1))
vid = data['props']['initialState']['play']['curVideoInfo']['vid']
```

**Key Data:**
```json
{
  "props": {
    "initialState": {
      "play": {
        "curVideoInfo": {
          "vid": "f7b8c9d0e1f2",
          "qipuId": "1234567890",
          "name": "Episode Title"
        }
      }
    }
  }
}
```

**Fields:**
- `vid`: Video ID (required for DASH API)
- `qipuId`: TV ID (same as from episode list)

---

### 4. DASH API (Subtitle Metadata)

**Purpose:** Get subtitle file URLs and metadata

**URL Format:** `https://cache-video.iq.com/dash?tvid={tvid}&vid={vid}&...&vf={vf}`

**Full Parameters:**
```python
params = {
    "tvid": tvid,                    # TV ID (qipuId)
    "bid": "",                       # Bid (empty)
    "vid": vid,                      # Video ID
    "src": "01011021010010000000",   # Source identifier
    "vt": "0",                       # Video type
    "rs": "1",                       # Related streams
    "uid": self.cookies.get('P00003', '0'),  # User ID
    "ori": "pcw",                    # Origin (PC web)
    "ps": "0",                       # Parameter set
    "k_uid": self.cookies['QC005'],  # Key user ID
    "pt": "0",                       # Platform type
    "d": "0",                        # Device
    "s": "",                         # Session
    "lid": "",                       # Locale ID
    "slid": "0",                     # Sub locale ID
    "cf": "",                        # Custom field
    "ct": "",                        # Custom type
    "authKey": self.get_auth_key(tvid),  # Generated auth key
    "k_tag": "1",                    # Key tag
    "ost": "0",                      # Other stream type
    "ppt": "0",                      # Platform parameter
    "dfp": self.cookies['__dfp'],    # Device fingerprint
    "locale": "zh_cn",               # Locale
    "prio": '{"ff":"","code":}',     # Priority
    "k_err_retries": "0",            # Error retries
    "qd_v": "2",                     # QD version
    "tm": int(time() * 1000),        # Timestamp (ms)
    "qdy": "a",                      # QDY
    "qds": "0",                      # QDS
    "k_ft1": "143486267424900",      # Feature flag 1
    "k_ft4": "1581060",              # Feature flag 4
    "k_ft7": "4",                    # Feature flag 7
    "k_ft5": "1",                    # Feature flag 5
    "bop": '{"version":"10.0","dfp":""}',  # BOP
    "ut": "1"                        # User type
}
```

**Request:**
```python
dash_url = self.get_dash_url(vid=vid, tvid=tvid)
res = self.session.get(url=dash_url, timeout=5)
```

**Success Response:**
```json
{
  "code": "A00000",
  "data": {
    "program": {
      "stl": [
        {
          "_name": "简体中文",
          "webvtt": "\\/subtitles\\/abc123\\/vtt\\/zh_cn.vtt",
          "xml": "\\/subtitles\\/abc123\\/xml\\/zh_cn.xml",
          "lang_code": "zh_cn"
        },
        {
          "_name": "English",
          "webvtt": "\\/subtitles\\/abc123\\/vtt\\/en.vtt",
          "xml": "\\/subtitles\\/abc123\\/xml\\/en.xml",
          "lang_code": "en"
        }
      ]
    }
  }
}
```

**Error Responses:**

**1. Invalid vf parameter:**
```json
{
  "code": "A00001",
  "data": {
    "boss_ts": {
      "msg": "vf validation failed"
    }
  }
}
```

**2. Region restriction:**
```json
{
  "code": "A00121",
  "msg": "This content is not available in your region"
}
```

**Fields:**
- `_name`: Display language name
- `webvtt`: VTT subtitle path (relative)
- `xml`: XML subtitle path (relative, backup)
- `lang_code`: Language code

**Subtitle URL Construction:**
```python
subtitle_link = self.config['api']['meta'] + sub['webvtt'].replace('\\/', '/')
# Result: https://meta.video.iqiyi.com/subtitles/abc123/vtt/zh_cn.vtt
```

---

### 5. Subtitle Download (Direct URL)

**Purpose:** Download actual subtitle files

**URL Format:** `https://meta.video.iqiyi.com{subtitle_path}`

**Example:** `https://meta.video.iqiyi.com/subtitles/abc123/vtt/zh_cn.vtt`

**Request:**
```python
subtitle_url = "https://meta.video.iqiyi.com/subtitles/abc123/vtt/zh_cn.vtt"
res = requests.get(subtitle_url)
```

**Response:**
- **VTT format:** WebVTT subtitle file
- **XML format:** iQIYI XML subtitle format (backup)

**Example VTT Content:**
```webvtt
WEBVTT
Kind: captions
Language: zh

00:00:01.000 --> 00:00:03.500
This is subtitle text

00:00:03.500 --> 00:00:06.000
Another subtitle line
```

## Data Structures

### Album Data Structure
```python
{
    'name': str,              # Content title
    'albumId': str,           # Album ID
    'year': str,              # Release year
    'videoType': str,         # 'singleVideo' or 'longVideo'
    'regionsAllowed': str,    # Comma-separated country codes
    'from': int,              # Starting episode
    'originalTotal': int,     # Total episodes
    'maxOrder': int           # Current available episodes
}
```

### Episode Data Structure
```python
{
    'qipuId': str,            # Episode ID (tvid)
    'order': int,             # Episode number
    'playLocSuffix': str,     # Play URL suffix
    'episodeType': int,       # Type filter
    'name': str               # Episode name
}
```

### Subtitle Metadata Structure
```python
{
    '_name': str,             # Display language name
    'webvtt': str,            # VTT file path
    'xml': str,               # XML file path (backup)
    'lang_code': str          # Language code
}
```

### Subtitle Download Queue Structure
```python
{
    'name': str,              # Filename
    'path': str,              # Download directory
    'url': str                # Download URL
}
```

## Request/Response Examples

### Complete Flow Example: Movie

**1. Initial Request:**
```
Input URL: https://www.iq.com/play/abc123-def456?lang=zh_tw
```

**2. Album Page Request:**
```http
GET /album/abc123 HTTP/1.1
Host: www.iq.com
User-Agent: Mozilla/5.0...
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz
```

**Response:** Extract video metadata and determine it's a movie

**3. Play Page Request:**
```http
GET /play/abc123-def456?lang=zh_tw HTTP/1.1
Host: www.iq.com
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz
```

**Response:** Extract `vid = "f7b8c9d0e1f2"`

**4. DASH API Request:**
```http
GET /dash?tvid=def456&vid=f7b8c9d0e1f2&...&vf=a1b2c3d4... HTTP/1.1
Host: cache-video.iq.com
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz
```

**Response:** Get subtitle URLs

**5. Subtitle Download:**
```http
GET /subtitles/abc123/vtt/zh_cn.vtt HTTP/1.1
Host: meta.video.iqiyi.com
```

**Response:** VTT file content

### Complete Flow Example: Series

**1. Initial Request:**
```
Input URL: https://www.iq.com/album/abc123
```

**2. Album Page Request:** (same as movie)

**3. Episode List Requests (multiple pages):**
```http
GET /api/v2/episodeListSource/abc123?platformId=3&modeCode=crystal&langCode=zh_tw&startOrder=1&endOrder=24 HTTP/1.1
Host: pcw-api.iq.com
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz
```

**Response:** Get 24 episodes

**4-6. For Each Episode:**
- Get vid from play page
- Get subtitle URLs from DASH API
- Add to download queue

**7. Download Subtitles:** (same as movie)

## Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| A00000 | Success | Continue processing |
| A00001 | vf validation failed | Check cookies, update cmd5x.js |
| A00121 | Region restricted | Use proxy from allowed region |
| A00138 | Video not available | Check video availability |
| A00203 | Invalid parameters | Verify tvid and vid |

### Handling Pattern
```python
res = self.session.get(url=dash_url)
if res.ok:
    data = res.json()['data']
    if 'program' in data:
        # Success - process subtitles
    elif 'boss_ts' in data:
        # Error - log and exit
        self.logger.error(data['boss_ts']['msg'])
    else:
        # Unknown error
        self.logger.error("Invalid dash_url, wrong vf!")
else:
    # HTTP error
    self.logger.error(res.text)
```

This comprehensive API reference covers all endpoints, authentication, data structures, and examples needed to understand and work with the iQIYI subtitle download system.
