# iQIYI Subtitle Downloader - Architecture Overview

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Class Structure](#class-structure)
3. [Main Workflow](#main-workflow)
4. [Key Components](#key-components)
5. [Dependencies](#dependencies)

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (URL)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   BaseService (Initialization)              │
│  - Cookie management                                         │
│  - Session configuration                                     │
│  - Proxy setup                                               │
│  - Language/Subtitle format settings                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     IQIYI Class                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  main() - Entry Point                               │    │
│  │  - URL validation & parsing                          │    │
│  │  - Content type detection (movie/series)            │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  movie_subtitle() - Movie Flow                      │    │
│  │  - Get video metadata                               │    │
│  │  - Extract video ID (vid)                           │    │
│  │  - Fetch subtitle URLs                              │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  series_subtitle() - Series Flow                    │    │
│  │  - Episode list retrieval                           │    │
│  │  - Multi-episode processing                         │    │
│  │  - Season/episode filtering                         │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Interaction Layer                      │
│  - Album/playlist page scraping                             │
│  - Episode list API calls                                   │
│  - DASH URL generation with authentication                  │
│  - Subtitle metadata extraction                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Subtitle Processing                          │
│  - get_subtitle() - Extract subtitle URLs                   │
│  - download_subtitle() - Download files                     │
│  - Format conversion (VTT → SRT/ASS)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Output Files                               │
│  - Individual subtitle files per language                   │
│  - Organized by series/season/episode                       │
└─────────────────────────────────────────────────────────────┘
```

## Class Structure

### IQIYI Class (services/iqiyi/iqiyi.py)

**Inheritance:** `IQIYI(BaseService)`

**Key Methods:**

1. **`__init__(self, args)`**
   - Initialize service with user arguments
   - Load locale settings
   - Inherit BaseService functionality

2. **`main(self)`** - Entry point
   - Parse input URL
   - Determine content type (movie vs series)
   - Route to appropriate handler

3. **`movie_subtitle(self, data)`** - Movie processing
   - Process single video content
   - Extract video information
   - Download subtitles

4. **`series_subtitle(self, data, mode_code, lang_code)`** - Series processing
   - Handle multi-episode content
   - Process episode lists
   - Filter by season/episode

5. **`get_vid(self, play_url)`** - Video ID extraction
   - Scrape play page for video ID
   - Parse JSON data from HTML

6. **`get_dash_url(self, vid, tvid)`** - DASH URL generation
   - Build authenticated DASH request URL
   - Generate auth key
   - Execute cmd5x.js for vf parameter

7. **`get_subtitle(self, data, folder_path, filename)`** - Subtitle extraction
   - Parse subtitle metadata
   - Filter by language
   - Build download list

8. **`download_subtitle(self, subtitles, languages, folder_path)`** - Download execution
   - Download subtitle files
   - Convert formats

9. **`get_auth_key(self, tvid)`** - Authentication
   - Generate MD5-based auth key

## Main Workflow

### 1. Initialization Phase
```
User runs command with URL
    ↓
BaseService.__init__()
    - Load configuration
    - Setup session with cookies
    - Configure proxy if needed
    - Set language preferences
    ↓
IQIYI.__init__()
    - Load locale strings
```

### 2. Content Detection Phase
```
IQIYI.main()
    ↓
Parse input URL
    ↓
Fetch album/playlist page
    ↓
Extract JSON from HTML:
    - modeCode
    - langCode
    - videoAlbumInfo
    ↓
Check videoType field:
    - "singleVideo" → movie_subtitle()
    - Otherwise → series_subtitle()
```

### 3. Movie Processing Flow
```
movie_subtitle()
    ↓
Extract title and year
    ↓
Get vid from get_vid(play_url)
    ↓
Generate DASH URL from get_dash_url()
    ↓
Fetch DASH data
    ↓
Extract subtitle metadata
    ↓
Filter by language preference
    ↓
Download and convert subtitles
```

### 4. Series Processing Flow
```
series_subtitle()
    ↓
Extract series metadata
    ↓
Calculate pagination for episode list
    ↓
Loop through pages:
    - Fetch episode list API
    - Accumulate episode data
    ↓
Filter episodes:
    - By season (download_season)
    - By episode (download_episode)
    - Last episode only option
    ↓
For each episode:
    - Get vid from play URL
    - Generate DASH URL
    - Fetch subtitle metadata
    - Add to download queue
    ↓
Download all subtitles
    ↓
Convert formats
```

## Key Components

### 1. Authentication System
- **Cookie-based authentication** using `__dfp` and `QC005` cookies
- **Dynamic auth key generation** using MD5 hashing
- **Timestamp-based validation** (current time in milliseconds)
- **vf parameter generation** via cmd5x.js (JavaScript execution)

### 2. API Endpoints
- **Episode List API:** `pcw-api.iq.com/api/v2/episodeListSource`
- **DASH API:** `cache-video.iq.com/dash`
- **Metadata Server:** `meta.video.iqiyi.com`

### 3. Data Parsing
- **HTML scraping** for embedded JSON data
- **JSON parsing** using orjson (fast JSON library)
- **Regex pattern matching** for data extraction

### 4. Subtitle Handling
- **Multi-language support** with filtering
- **Format conversion** (XML/VTT → SRT/ASS)
- **File organization** by language and content type

## Dependencies

### Python Libraries
- **orjson** - Fast JSON parsing
- **requests** - HTTP client
- **hashlib** - MD5 authentication
- **re** - Regex pattern matching
- **subprocess** - Node.js execution for cmd5x.js

### External Dependencies
- **Node.js** - Required for cmd5x.js execution
- **cmd5x.js** - iQIYI's vf parameter generation script
- **Cookie file** - Authentication cookies from browser

### Configuration Files
- **user_config.toml** - Main configuration
- **configs/iQIYI.toml** - Service-specific settings
- **cookies/www.iq.com_cookies.txt** - Authentication

## Data Flow Summary

```
Input URL
    ↓
Album Page (HTML + embedded JSON)
    ↓
Episode List API (for series)
    ↓
Play Page Scrape (for vid)
    ↓
DASH API (with auth)
    ↓
Subtitle URLs (VTT/XML)
    ↓
Download & Convert
    ↓
Final Subtitle Files
```

This architecture enables reliable subtitle extraction from iQIYI while handling authentication, geofencing, and various content types (movies and series with multiple seasons/episodes).
