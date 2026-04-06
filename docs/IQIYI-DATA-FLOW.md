# iQIYI Subtitle Downloader - Complete Data Flow & Logging

## Table of Contents
1. [Complete Data Flow Diagram](#complete-data-flow-diagram)
2. [Step-by-Step Data Flow](#step-by-step-data-flow)
3. [API Call Sequence](#api-call-sequence)
4. [Data Transformations](#data-transformations)
5. [Complete Request/Response Logging](#complete-requestresponse-logging)

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INPUT                                   │
│  URL: https://www.iq.com/play/abc123-def456?lang=zh_tw         │
│  Options: --subtitle-language all,en,zh --season 1 --episode 1,2│
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: URL PARSING & CONTENT TYPE DETECTION                   │
│  Location: main() - Line 333-371                               │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - User URL (play or album format)                           │
│    - Cookies from file                                         │
│    - Session configuration                                     │
│                                                                 │
│  Process:                                                       │
│    1. Check if URL contains 'play/'                            │
│       If yes → Extract content_id and convert to album URL     │
│       Regex: r'https://www.iq.com/play/.+\-([^-]+)\?lang=.+'   │
│                                                                 │
│    2. GET request to album URL                                 │
│       URL: https://www.iq.com/album/{content_id}               │
│                                                                 │
│    3. Extract JSON from HTML response                          │
│       Regex: r'({\"props\":{.*})'                              │
│                                                                 │
│    4. Parse JSON to get:                                       │
│       - modeCode (e.g., "crystal")                             │
│       - langCode (e.g., "zh_tw")                               │
│       - videoAlbumInfo object                                  │
│                                                                 │
│    5. Determine content type:                                  │
│       - videoType == "singleVideo" → MOVIE                     │
│       - videoType != "singleVideo" → SERIES                    │
│                                                                 │
│  Output:                                                        │
│    - modeCode: "crystal"                                       │
│    - langCode: "zh_tw"                                         │
│    - data: {                                                   │
│        name: "Content Name",                                   │
│        albumId: "abc123",                                      │
│        year: "2023",                                           │
│        videoType: "singleVideo" or "longVideo",               │
│        regionsAllowed: "tw,hk,my",                             │
│        from: 1,                                                │
│        originalTotal: 20,                                      │
│        maxOrder: 20                                            │
│      }                                                         │
│                                                                 │
│  API Call #1:                                                   │
│    GET https://www.iq.com/album/{content_id}                   │
│    Headers: {User-Agent, Cookies}                              │
│    Response: HTML with embedded JSON                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   Content Type?       │
                    └───────────┬───────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
        ┌───────────────┐               ┌───────────────┐
        │    MOVIE      │               │    SERIES     │
        │   FLOW        │               │    FLOW       │
        └───────────────┘               └───────────────┘
                │                               │
                ▼                               ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 2A: MOVIE FLOW - movie_subtitle()                         │
│  Location: Line 59-100                                          │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - data (from step 1)                                        │
│                                                                 │
│  Process:                                                       │
│    1. Extract title and year                                   │
│       title = data['name'].strip()                             │
│       release_year = data['year']                              │
│                                                                 │
│    2. Create folder structure                                  │
│       folder_path = downloads/{Title.Year}                     │
│       filename = {Title.Year}.WEB-DL.iqiyi.vtt                 │
│                                                                 │
│    3. Get play URL                                             │
│       play_url = f"https:{data['playUrl']}"                    │
│                                                                 │
│    4. Get vid using get_vid()                                  │
│       → See STEP 3                                             │
│                                                                 │
│    5. Get DASH URL using get_dash_url()                        │
│       → See STEP 4                                             │
│                                                                 │
│    6. Fetch DASH data                                          │
│       → See STEP 5                                             │
│                                                                 │
│  Output:                                                        │
│    - Subtitles downloaded and converted                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 2B: SERIES FLOW - series_subtitle()                       │
│  Location: Line 101-216                                         │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - data (from step 1)                                        │
│    - modeCode (from step 1)                                    │
│    - langCode (from step 1)                                    │
│                                                                 │
│  Process:                                                       │
│    1. Extract series metadata                                  │
│       title = data['name'].strip()                             │
│       album_id = data['albumId']                               │
│       start_order = data['from'] (default: 1)                  │
│       episode_num = data['originalTotal']                      │
│       current_eps = data.get('maxOrder', episode_num)          │
│                                                                 │
│    2. Parse title and season index                             │
│       title, season_index = get_title_and_season_index(title)  │
│       → Extracts "Season 1" or "S01" from title                │
│                                                                 │
│    3. Calculate pagination                                     │
│       page_size = math.ceil(current_eps / 24)                  │
│       Example: 50 episodes → 3 pages                           │
│                                                                 │
│    4. Loop through pages to get episode list                   │
│       FOR page in 0 to page_size-1:                            │
│         start_order = page * 24 + 1                            │
│         end_order = min((page+1) * 24, current_eps)            │
│                                                                 │
│         Build episode_list_url:                                │
│         https://pcw-api.iq.com/api/v2/episodeListSource/       │
│         {album_id}?platformId=3&modeCode={mode_code}&          │
│         langCode={lang_code}&...&startOrder={start_order}&     │
│         endOrder={end_order}                                   │
│                                                                 │
│         GET request to episode_list_url                        │
│         → See STEP 2B-1                                        │
│                                                                 │
│         Accumulate episodes: episode_list += response['data']['epg']│
│                                                                 │
│    5. Filter episodes                                          │
│       IF last_episode:                                         │
│         episode_list = [last episode only]                     │
│                                                                 │
│       FOR each episode in episode_list:                        │
│         IF episode['episodeType'] in [1, 6]:                   │
│           CONTINUE (skip trailers, previews)                   │
│                                                                 │
│         episode_index = episode['order']                       │
│         IF episode_index == -1: episode_index = 0              │
│                                                                 │
│         Check filters:                                         │
│         IF download_season AND season_index NOT in download_season:│
│           CONTINUE                                             │
│         IF download_episode AND episode_index NOT in download_episode:│
│           CONTINUE                                             │
│                                                                 │
│    6. Process each episode                                     │
│       FOR each filtered episode:                               │
│         filename = {Title.S01E02}.WEB-DL.iqiyi.vtt             │
│                                                                 │
│         tvid = episode['qipuId']                               │
│         play_url = f"https://www.iq.com/play/{episode['playLocSuffix']}"│
│                                                                 │
│         Get vid using get_vid(play_url)                        │
│         → See STEP 3                                           │
│                                                                 │
│         Get DASH URL using get_dash_url(vid, tvid)             │
│         → See STEP 4                                           │
│                                                                 │
│         Fetch DASH data                                        │
│         → See STEP 5                                           │
│                                                                 │
│  Output:                                                        │
│    - Multiple episode subtitles downloaded and converted       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 2B-1: EPISODE LIST API CALL                               │
│  Location: Line 127-138                                         │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - album_id                                                  │
│    - mode_code                                                 │
│    - lang_code                                                 │
│    - start_order (1, 25, 49, ...)                             │
│    - end_order (24, 48, 50, ...)                              │
│                                                                 │
│  API Call #2 (Series only, multiple calls):                    │
│    GET https://pcw-api.iq.com/api/v2/episodeListSource/        │
│        {album_id}?platformId=3&modeCode={mode_code}&           │
│        langCode={lang_code}&deviceId=21fcb553c8e206bb515b497bb6376aa4&│
│        endOrder={end_order}&startOrder={start_order}           │
│                                                                 │
│  Example:                                                       │
│    https://pcw-api.iq.com/api/v2/episodeListSource/abc123?     │
│    platformId=3&modeCode=crystal&langCode=zh_tw&               │
│    deviceId=21fcb553c8e206bb515b497bb6376aa4&                   │
│    endOrder=24&startOrder=1                                    │
│                                                                 │
│  Response Data:                                                 │
│    {                                                           │
│      "code": "A00000",                                         │
│      "data": {                                                 │
│        "epg": [                                                │
│          {                                                     │
│            "qipuId": "1234567890",                             │
│            "order": 1,                                         │
│            "playLocSuffix": "abc123-1234567890?lang=zh_tw",    │
│            "episodeType": 0,                                   │
│            "name": "Episode 1"                                 │
│          },                                                    │
│          ... (up to 24 episodes)                               │
│        ]                                                       │
│      }                                                         │
│    }                                                           │
│                                                                 │
│  Output:                                                        │
│    - episode_list array with up to 24 episodes per page        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: GET VIDEO ID (vid) - get_vid()                        │
│  Location: Line 36-57                                           │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - play_url (e.g., https://www.iq.com/play/abc123-1234567890?lang=zh_tw)│
│                                                                 │
│  Process:                                                       │
│    1. Sleep 2 seconds (rate limiting)                          │
│       sleep(2)                                                 │
│                                                                 │
│    2. GET request to play_url                                  │
│       res = self.session.get(play_url, timeout=5)              │
│                                                                 │
│    3. Check response                                           │
│       IF NOT res.ok:                                           │
│         Log error and exit                                     │
│                                                                 │
│    4. Extract JSON from HTML                                   │
│       match = re.search(r'({\"props\":{.*})', res.text)        │
│                                                                 │
│       IF NOT match:                                            │
│         Log "Please input correct play url!"                   │
│         Exit                                                   │
│                                                                 │
│    5. Parse JSON                                               │
│       data = orjson.loads(match.group(1))                      │
│                                                                 │
│    6. Extract vid                                              │
│       vid = data['props']['initialState']['play']['curVideoInfo']['vid']│
│                                                                 │
│       IF NOT vid:                                              │
│         Log "Can't find vid!"                                  │
│         Exit                                                   │
│                                                                 │
│  API Call #3 (Per video/episode):                              │
│    GET https://www.iq.com/play/{playLocSuffix}                 │
│    Headers: {User-Agent, Cookies}                              │
│    Response: HTML with embedded JSON                           │
│                                                                 │
│  Response Data Structure:                                      │
│    {                                                           │
│      "props": {                                                │
│        "initialState": {                                       │
│          "play": {                                             │
│            "curVideoInfo": {                                   │
│              "vid": "f7b8c9d0e1f2",                            │
│              "qipuId": "1234567890",                           │
│              "name": "Episode Title"                           │
│            }                                                   │
│          }                                                     │
│        }                                                       │
│      }                                                         │
│    }                                                           │
│                                                                 │
│  Output:                                                        │
│    - vid: "f7b8c9d0e1f2" (12-character hex string)             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: GENERATE DASH URL - get_dash_url()                     │
│  Location: Line 224-276                                         │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - vid (from step 3)                                         │
│    - tvid (from episode data)                                  │
│    - cookies (from initialization)                            │
│                                                                 │
│  Process:                                                       │
│    1. Generate authKey                                         │
│       → See STEP 4A                                           │
│       authKey = get_auth_key(tvid)                             │
│                                                                 │
│    2. Build DASH URL parameters                                │
│       params = {                                               │
│         "tvid": tvid,                                          │
│         "vid": vid,                                            │
│         "src": "01011021010010000000",                         │
│         "uid": cookies.get('P00003', '0'),                     │
│         "k_uid": cookies['QC005'],                             │
│         "dfp": cookies['__dfp'],                               │
│         "authKey": authKey,                                    │
│         "tm": int(time() * 1000),                              │
│         "ori": "pcw",                                           │
│         "locale": "zh_cn",                                     │
│         ... (20+ more parameters)                              │
│       }                                                        │
│                                                                 │
│    3. URL encode parameters                                    │
│       url = "/dash?" + urlencode(params)                       │
│       Result: "/dash?tvid=123&vid=abc&..."                     │
│                                                                 │
│    4. Generate vf parameter using Node.js                      │
│       → See STEP 4B                                           │
│       cmdx5js_path = services/iqiyi/cmd5x.js                   │
│       process = subprocess.run([node_executable, cmdx5js, url])│
│       vf = process.stdout.decode("utf-8").strip()              │
│                                                                 │
│    5. Build final DASH URL                                     │
│       dash_url = f"https://cache-video.iq.com{url}&vf={vf}"    │
│                                                                 │
│  No direct API call in this step - URL construction only       │
│                                                                 │
│  Output:                                                        │
│    - dash_url: "https://cache-video.iq.com/dash?tvid=123&vid=abc&...&vf=a1b2c3..."│
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 4A: GENERATE AUTH KEY - get_auth_key()                    │
│  Location: Line 218-222                                         │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - tvid (e.g., "1234567890")                                 │
│    - Current timestamp (auto-generated)                        │
│                                                                 │
│  Process:                                                       │
│    1. Build text string                                        │
│       text = f"d41d8cd98f00b204e9800998ecf8427e{timestamp_ms}{tvid}"│
│                                                                 │
│       Example:                                                 │
│         timestamp = 1699776000000                              │
│         tvid = "1234567890"                                    │
│         text = "d41d8cd98f00b204e9800998ecf8427e16997760000001234567890"│
│                                                                 │
│    2. Calculate MD5 hash                                       │
│       md = md5()                                               │
│       md.update(text.encode())                                 │
│       auth_key = md.hexdigest()                                │
│                                                                 │
│  Output:                                                        │
│    - auth_key: "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6" (32-char hex)│
│                                                                 │
│  Example Calculation:                                          │
│    Input: "d41d8cd98f00b204e9800998ecf8427e16997760000001234567890"│
│    MD5:   5d41402abc4b2a76b9719d911017c592                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 4B: GENERATE VF PARAMETER - cmd5x.js                      │
│  Location: External file (services/iqiyi/cmd5x.js)             │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - URL-encoded DASH parameters string                        │
│    Example: "/dash?tvid=123&vid=abc&...&tm=1699776000000"     │
│                                                                 │
│  Process:                                                       │
│    1. Execute Node.js script                                   │
│       node /path/to/cmd5x.js "/dash?..."                       │
│                                                                 │
│    2. cmd5x.js processes:                                      │
│       - Parse URL parameters                                   │
│       - Apply proprietary algorithm                            │
│       - Generate vf validation parameter                       │
│                                                                 │
│    3. Capture stdout                                           │
│       vf = process.stdout output                               │
│                                                                 │
│  Output:                                                        │
│    - vf: "1386623822_123456_abc...def" (variable length)      │
│                                                                 │
│  Note: cmd5x.js contains obfuscated JavaScript (35KB+)         │
│        implementing iQIYI's proprietary validation algorithm   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: FETCH SUBTITLE METADATA - DASH API                     │
│  Location: movie_subtitle() Line 84-99, series_subtitle() Line 188-213│
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - dash_url (from step 4)                                    │
│                                                                 │
│  Process:                                                       │
│    1. GET request to dash_url                                  │
│       res = self.session.get(url=dash_url, timeout=5)          │
│                                                                 │
│    2. Check response status                                    │
│       IF NOT res.ok:                                           │
│         Log error and exit                                     │
│                                                                 │
│    3. Parse JSON response                                      │
│       movie_data = res.json()['data']                          │
│                                                                 │
│    4. Check for program data                                   │
│       IF 'program' in movie_data:                              │
│         program_data = movie_data['program']                   │
│         → Process subtitles (STEP 6)                          │
│                                                                 │
│       ELSE IF 'boss_ts' in movie_data:                         │
│         Log error: movie_data['boss_ts']['msg']                │
│         (Error: vf validation failed, region restriction, etc.) │
│                                                                 │
│       ELSE:                                                    │
│         Log "Invalid dash_url, wrong vf!"                      │
│         Log "Renew your cookies and try again!"                │
│         Exit                                                   │
│                                                                 │
│  API Call #4 (Per video/episode):                              │
│    GET https://cache-video.iq.com/dash?tvid={tvid}&vid={vid}&...&vf={vf}│
│    Headers: {User-Agent, Cookies}                              │
│    Response: JSON with subtitle metadata                       │
│                                                                 │
│  Response Data Structure (Success):                            │
│    {                                                           │
│      "code": "A00000",                                         │
│      "data": {                                                 │
│        "program": {                                            │
│          "stl": [                                              │
│            {                                                   │
│              "_name": "简体中文",                               │
│              "webvtt": "\\/subtitles\\/abc123\\/vtt\\/zh_cn.vtt",│
│              "xml": "\\/subtitles\\/abc123\\/xml\\/zh_cn.xml", │
│              "lang_code": "zh_cn"                              │
│            },                                                  │
│            {                                                   │
│              "_name": "English",                               │
│              "webvtt": "\\/subtitles\\/abc123\\/vtt\\/en.vtt", │
│              "xml": "\\/subtitles\\/abc123\\/xml\\/en.xml",    │
│              "lang_code": "en"                                 │
│            }                                                   │
│          ]                                                     │
│        }                                                       │
│      }                                                         │
│    }                                                           │
│                                                                 │
│  Response Data Structure (Error):                              │
│    {                                                           │
│      "code": "A00001",                                         │
│      "data": {                                                 │
│        "boss_ts": {                                            │
│          "msg": "vf validation failed"                         │
│        }                                                       │
│      }                                                         │
│    }                                                           │
│                                                                 │
│  Output:                                                        │
│    - program_data with subtitle metadata array                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: EXTRACT SUBTITLE URLS - get_subtitle()                 │
│  Location: Line 278-322                                         │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - program_data (from step 5)                                │
│    - folder_path (download directory)                         │
│    - filename (base filename)                                 │
│    - subtitle_language (user preference: all, en, zh, etc.)   │
│                                                                 │
│  Process:                                                       │
│    1. Check if subtitles exist                                 │
│       IF 'stl' NOT in program_data:                            │
│         Log "Sorry, there's no embedded subtitles!"            │
│         Return empty lists                                     │
│                                                                 │
│    2. Initialize variables                                     │
│       lang_paths = set()  # Track language folders used        │
│       subtitles = []     # Download queue                      │
│       available_languages = set()  # All available languages   │
│                                                                 │
│    3. Loop through each subtitle track                         │
│       FOR sub in program_data['stl']:                          │
│                                                                 │
│         a. Extract and normalize language code                 │
│            sub_lang = get_language_code(sub['_name'])          │
│            Example: "简体中文" → "zh_cn"                       │
│                     "English" → "en"                           │
│                                                                 │
│         b. Track available language                            │
│            available_languages.add(sub_lang)                   │
│                                                                 │
│         c. Check if language matches user preference           │
│            IF sub_lang in subtitle_language OR 'all' in subtitle_language:│
│                                                                 │
│            d. Determine folder structure                       │
│               IF len(subtitle_language) > 1 OR 'all' in subtitle_language:│
│                 lang_folder_path = folder_path / sub_lang      │
│                 Example: downloads/Movie.Name.2023/zh_cn/     │
│               ELSE:                                            │
│                 lang_folder_path = folder_path                 │
│                 Example: downloads/Movie.Name.2023/           │
│                                                                 │
│            e. Add to language paths                            │
│               lang_paths.add(lang_folder_path)                 │
│                                                                 │
│            f. Determine subtitle format and filename           │
│               IF 'webvtt' in sub:                              │
│                 subtitle_link = sub['webvtt']                  │
│                 subtitle_filename = filename.replace('.vtt', f'.{sub_lang}.vtt')│
│               ELSE:                                            │
│                 subtitle_link = sub['xml']                     │
│                 subtitle_filename = filename.replace('.vtt', f'.{sub_lang}.xml')│
│                                                                 │
│            g. Build full subtitle URL                          │
│               subtitle_link = config['api']['meta'] + subtitle_link.replace('\\/', '/')│
│               Example: https://meta.video.iqiyi.com/subtitles/abc123/vtt/zh_cn.vtt│
│                                                                 │
│            h. Create download directory                        │
│               os.makedirs(lang_folder_path, exist_ok=True)     │
│                                                                 │
│            i. Add to download queue                            │
│               subtitle = {                                     │
│                 'name': subtitle_filename,                     │
│                 'path': lang_folder_path,                      │
│                 'url': subtitle_link                           │
│               }                                                │
│               subtitles.append(subtitle)                       │
│                                                                 │
│    4. Display available languages to user                     │
│       get_all_languages(                                      │
│         available_languages=available_languages,               │
│         subtitle_language=subtitle_language,                   │
│         locale_=self.locale                                    │
│       )                                                        │
│                                                                 │
│  No API call in this step - data processing only               │
│                                                                 │
│  Output:                                                        │
│    - subtitles: [                                              │
│        {name: "Movie.2023.zh_cn.vtt", path: ".../zh_cn", url: "https://..."},│
│        {name: "Movie.2023.en.vtt", path: ".../en", url: "https://..."}│
│      ]                                                         │
│    - lang_paths: {"downloads/Movie.2023/zh_cn", "downloads/Movie.2023/en"}│
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼

┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: DOWNLOAD SUBTITLES - download_subtitle()               │
│  Location: Line 324-331                                         │
├─────────────────────────────────────────────────────────────────┤
│  Input:                                                         │
│    - subtitles (download queue from step 6)                   │
│    - lang_paths (set of language folders)                     │
│    - folder_path (base download directory)                    │
│    - subtitle_format (output format: .srt, .ass, .vtt)        │
│                                                                 │
│  Process:                                                       │
│    1. Check if there are subtitles to download                 │
│       IF NOT subtitles OR NOT lang_paths:                      │
│         Return (nothing to do)                                 │
│                                                                 │
│    2. Download all subtitle files                              │
│       download_files(subtitles)                                │
│       → Helper function that:                                  │
│         - Iterates through subtitles list                      │
│         - Downloads each file from URL to path/name            │
│         - Shows progress bar                                   │
│         - Handles download errors                              │
│                                                                 │
│    3. Convert subtitles for each language folder               │
│       FOR lang_path in sorted(lang_paths):                     │
│         convert_subtitle(                                     │
│           folder_path=lang_path,                               │
│           subtitle_format=self.subtitle_format,                │
│           locale=self.locale                                   │
│         )                                                      │
│         → Helper function that:                                │
│           - Converts VTT/XML to requested format               │
│           - Fixes common subtitle issues                       │
│           - Creates .srt, .ass, or keeps .vtt                  │
│                                                                 │
│    4. Convert combined subtitles in base folder               │
│       convert_subtitle(                                       │
│         folder_path=folder_path,                               │
│         platform=self.platform,                                │
│         subtitle_format=self.subtitle_format,                  │
│         locale=self.locale                                     │
│       )                                                        │
│                                                                 │
│  API Call #5 (Per subtitle file):                              │
│    GET https://meta.video.iqiyi.com/subtitles/{id}/vtt/{lang}.vtt│
│    Headers: {User-Agent}                                       │
│    Response: Subtitle file content (VTT or XML)                │
│                                                                 │
│  Example Subtitle Downloads:                                   │
│    GET https://meta.video.iqiyi.com/subtitles/abc123/vtt/zh_cn.vtt│
│    → Save to: downloads/Movie.2023/zh_cn/Movie.2023.zh_cn.vtt │
│                                                                 │
│    GET https://meta.video.iqiyi.com/subtitles/abc123/vtt/en.vtt│
│    → Save to: downloads/Movie.2023/en/Movie.2023.en.vtt       │
│                                                                 │
│  Output:                                                        │
│    - Downloaded subtitle files in VTT format                   │
│    - Converted subtitle files in requested format (SRT/ASS/VTT)│
│    - File structure:                                           │
│      downloads/                                                │
│        Movie.Name.2023/                                       │
│          Movie.Name.2023.zh_cn.srt                            │
│          Movie.Name.2023.en.srt                               │
│          zh_cn/                                               │
│            Movie.Name.2023.zh_cn.vtt (original)               │
│          en/                                                  │
│            Movie.Name.2023.en.vtt (original)                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     COMPLETE                                    │
│  All subtitles downloaded and converted successfully           │
└─────────────────────────────────────────────────────────────────┘
```

## API Call Summary Table

| Step | API Call | Times | Purpose | Input | Output |
|------|----------|-------|---------|-------|--------|
| 1 | Album page | 1 | Get content metadata | Album URL | Content info, mode/lang codes |
| 2B-1 | Episode list | 1-N | Get episode list (series only) | Album ID + pagination | Episode array |
| 3 | Play page | 1-N | Extract video ID | Play URL | vid |
| 4 | DASH URL gen | 1-N | Build authenticated URL | vid, tvid, cookies | DASH URL with vf |
| 5 | DASH API | 1-N | Get subtitle metadata | DASH URL | Subtitle URLs |
| 7 | Subtitle download | 1-M | Download subtitle files | Subtitle URLs | Subtitle files |

**Legend:**
- 1 = Once per run
- N = Once per video/episode
- M = Once per subtitle file

## Complete Request/Response Examples

### Example 1: Movie Download

**User Input:**
```
URL: https://www.iq.com/play/movie-abc123?lang=zh_tw
Languages: all
Format: srt
```

**Step-by-Step Execution:**

**Step 1: Album Page**
```http
GET /album/movie-abc123 HTTP/1.1
Host: www.iq.com
User-Agent: Mozilla/5.0...
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz

Response (HTML excerpt):
<script>
  self.__state = {"props":{
    "initialProps":{
      "pageProps":{
        "modeCode":"crystal",
        "langCode":"zh_tw"
      }
    },
    "initialState":{
      "album":{
        "videoAlbumInfo":{
          "name":"Test Movie",
          "albumId":"movie-abc123",
          "year":"2023",
          "videoType":"singleVideo",
          "regionsAllowed":"tw,hk,my",
          "playUrl":"//www.iq.com/play/movie-abc123-def456?lang=zh_tw"
        }
      }
    }
  }}
</script>
```

**Step 3: Play Page (get vid)**
```http
GET /play/movie-abc123-def456?lang=zh_tw HTTP/1.1
Host: www.iq.com
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz

Response (HTML excerpt):
<script>
  self.__state = {"props":{
    "initialState":{
      "play":{
        "curVideoInfo":{
          "vid":"f7b8c9d0e1f2",
          "qipuId":"def456"
        }
      }
    }
  }}
</script>
```

**Step 4: Generate DASH URL**
```python
authKey = get_auth_key("def456")
# authKey = "5d41402abc4b2a76b9719d911017c592"

params = {
    "tvid": "def456",
    "vid": "f7b8c9d0e1f2",
    "authKey": "5d41402abc4b2a76b9719d911017c592",
    "tm": 1699776000000,
    ... # 20+ more params
}

url = "/dash?" + urlencode(params)
vf = execute_cmd5x(url)
# vf = "1386623822_def456_f7b8c9d0..."

dash_url = "https://cache-video.iq.com/dash?tvid=def456&vid=f7b8c9d0e1f2&...&vf=1386623822_def456_f7b8c9d0..."
```

**Step 5: DASH API**
```http
GET /dash?tvid=def456&vid=f7b8c9d0e1f2&...&vf=1386623822_def456_f7b8c9d0... HTTP/1.1
Host: cache-video.iq.com
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz

Response:
{
  "code": "A00000",
  "data": {
    "program": {
      "stl": [
        {
          "_name": "简体中文",
          "webvtt": "\\/subtitles\\/movie-abc123\\/vtt\\/zh_cn.vtt",
          "xml": "\\/subtitles\\/movie-abc123\\/xml\\/zh_cn.xml",
          "lang_code": "zh_cn"
        },
        {
          "_name": "English",
          "webvtt": "\\/subtitles\\/movie-abc123\\/vtt\\/en.vtt",
          "xml": "\\/subtitles\\/movie-abc123\\/xml\\/en.xml",
          "lang_code": "en"
        }
      ]
    }
  }
}
```

**Step 6: Extract Subtitle URLs**
```python
# For Chinese subtitle
subtitle_link = "https://meta.video.iqiyi.com" + "/subtitles/movie-abc123/vtt/zh_cn.vtt"
subtitle_filename = "Test.Movie.2023.zh_cn.vtt"
lang_folder_path = "downloads/Test.Movie.2023/zh_cn"

# For English subtitle
subtitle_link = "https://meta.video.iqiyi.com" + "/subtitles/movie-abc123/vtt/en.vtt"
subtitle_filename = "Test.Movie.2023.en.vtt"
lang_folder_path = "downloads/Test.Movie.2023/en"
```

**Step 7: Download Subtitles**
```http
GET /subtitles/movie-abc123/vtt/zh_cn.vtt HTTP/1.1
Host: meta.video.iqiyi.com

Response:
WEBVTT
Kind: captions
Language: zh

00:00:01.000 --> 00:00:03.500
这是中文字幕

00:00:03.500 --> 00:00:06.000
第二行字幕
```

```http
GET /subtitles/movie-abc123/vtt/en.vtt HTTP/1.1
Host: meta.video.iqiyi.com

Response:
WEBVTT
Kind: captions
Language: en

00:00:01.000 --> 00:00:03.500
This is English subtitle

00:00:03.500 --> 00:00:06.000
Second subtitle line
```

**Final Output Structure:**
```
downloads/
  Test.Movie.2023/
    Test.Movie.2023.zh_cn.srt  (converted from VTT)
    Test.Movie.2023.en.srt     (converted from VTT)
    zh_cn/
      Test.Movie.2023.zh_cn.vtt (original)
    en/
      Test.Movie.2023.en.vtt    (original)
```

### Example 2: Series Download (Episode 1-2)

**User Input:**
```
URL: https://www.iq.com/album/series-abc123
Languages: zh_cn,en
Format: srt
Season: 1
Episode: 1,2
```

**Step 1: Album Page**
[Similar to movie, but videoType="longVideo"]

**Step 2B-1: Episode List (Page 1)**
```http
GET /api/v2/episodeListSource/series-abc123?platformId=3&modeCode=crystal&langCode=zh_tw&deviceId=21fcb553c8e206bb515b497bb6376aa4&endOrder=24&startOrder=1 HTTP/1.1
Host: pcw-api.iq.com
Cookie: __dfp=xxx; QC005=yyy; P00003=zzz

Response:
{
  "code": "A00000",
  "data": {
    "epg": [
      {
        "qipuId": "ep001",
        "order": 1,
        "playLocSuffix": "series-abc123-ep001?lang=zh_tw",
        "episodeType": 0,
        "name": "Episode 1"
      },
      {
        "qipuId": "ep002",
        "order": 2,
        "playLocSuffix": "series-abc123-ep002?lang=zh_tw",
        "episodeType": 0,
        "name": "Episode 2"
      },
      ... (episodes 3-24)
    ]
  }
}
```

**Step 3-7: For Episode 1**
[Same process as movie, repeated for each episode]

**Step 3-7: For Episode 2**
[Same process as movie, repeated for each episode]

**Final Output Structure:**
```
downloads/
  Series.Name.S01/
    Series.Name.S01E01.zh_cn.srt
    Series.Name.S01E01.en.srt
    Series.Name.S01E02.zh_cn.srt
    Series.Name.S01E02.en.srt
```

## Data Transformations Summary

### URL Transformations
1. Play URL → Album URL: Extract album_id
2. Album URL → Content metadata: Parse JSON from HTML
3. Episode data → Play URL: Prepend "https://www.iq.com/play/"
4. DASH parameters → DASH URL: URL encode + add vf parameter
5. Relative subtitle path → Absolute URL: Prepend metadata domain

### Data Format Transformations
1. HTML → JSON: Regex extraction + orjson parsing
2. JSON → Python dict: orjson loads
3. vid + tvid → authKey: MD5 hash calculation
4. DASH URL → vf parameter: Node.js execution
5. VTT/XML → SRT/ASS: Subtitle conversion utility

### Language Code Transformations
1. Display name → Language code: "简体中文" → "zh_cn"
2. Language filtering: Check against user preferences
3. Filename generation: Append language code to base filename

This complete data flow documentation provides a comprehensive view of every step, API call, and data transformation in the iQIYI subtitle download process.
