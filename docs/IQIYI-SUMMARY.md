# iQIYI Subtitle Downloader - Documentation Summary

## Overview

This documentation set provides comprehensive analysis and documentation of the iQIYI subtitle downloader implementation at `/Users/baagas0/Documents/project/subtitle-downloader/services/iqiyi/iqiyi.py`.

## Document Structure

The documentation is organized into four separate documents, each focusing on a specific aspect of the system:

### 1. IQIYI-ARCHITECTURE.md
**Focus:** System architecture and design

**Contents:**
- High-level system architecture diagram
- Class structure and inheritance
- Main workflow overview
- Key components explanation
- Dependencies and requirements
- Data flow summary

**Best for:** Understanding the big picture and how components interact

---

### 2. IQIYI-API-REFERENCE.md
**Focus:** API endpoints and technical specifications

**Contents:**
- Complete API endpoints documentation
- Authentication mechanism details
- Request/response formats
- Data structures
- Error codes and handling
- Parameter reference

**Best for:** Understanding API calls and implementing similar functionality

---

### 3. IQIYI-DATA-FLOW.md
**Focus:** Detailed execution flow and data transformations

**Contents:**
- Step-by-step data flow with ASCII diagrams
- Complete request/response logging
- Data transformation explanations
- API call sequence
- Real-world examples

**Best for:** Understanding exactly what happens during execution and debugging

---

### 4. IQIYI-IMPLEMENTATION-GUIDE.md
**Focus:** Setup, usage, and practical guidance

**Contents:**
- Installation and setup
- Configuration details
- Authentication setup with cookies
- Command-line usage
- Troubleshooting guide
- Advanced usage patterns
- Development and extension guidelines

**Best for:** Actually using the tool and solving problems

---

## Key Findings from Analysis

### How iQIYI Subtitle Download Works

**Authentication Method:**
- Cookie-based authentication using browser-exported cookies
- Required cookies: `__dfp` (device fingerprint), `QC005` (auth key), `P00003` (session)
- Dynamic auth key generation using MD5 hashing
- VF parameter generation via Node.js execution of cmd5x.js

**API Endpoints Used:**
1. **Album Page** - Get content metadata
2. **Episode List API** - Get episode list for series
3. **Play Page** - Extract video ID (vid)
4. **DASH API** - Get subtitle metadata with authentication
5. **Subtitle Download** - Direct file downloads

**Core Workflow:**
```
User URL
  → Extract album info
  → Get episode list (if series)
  → For each video:
    → Extract vid from play page
    → Generate authenticated DASH URL
    → Fetch subtitle metadata
    → Download subtitle files
    → Convert to requested format
```

**Key Data Transformations:**
1. HTML → JSON (regex extraction)
2. Video metadata → vid (JSON parsing)
3. vid + tvid → authKey (MD5 hash)
4. DASH parameters → vf parameter (Node.js)
5. VTT/XML → SRT/ASS (conversion)

### Security and Anti-Scraping Measures

**Obfuscation:**
- cmd5x.js is a 35KB+ obfuscated JavaScript file
- Implements proprietary validation algorithm
- Required for generating vf parameter

**Validation:**
- Timestamp-based authentication (prevents replay attacks)
- Device fingerprint validation (__dfp)
- Multi-parameter validation (20+ parameters in DASH request)

**Rate Limiting:**
- Built-in 2-second delay between play page requests
- Prevents excessive API calls

### API Calls Summary

| Step | API | Frequency | Purpose |
|------|-----|-----------|---------|
| 1 | Album page | 1/run | Get content metadata |
| 2 | Episode list | 1-N/run | Get episode list (series) |
| 3 | Play page | 1-N/run | Extract video ID |
| 4 | DASH URL gen | 1-N/run | Build authenticated URL |
| 5 | DASH API | 1-N/run | Get subtitle metadata |
| 6 | Subtitle download | 1-M/run | Download files |

**Legend:**
- 1 = Once per run
- N = Once per video/episode
- M = Once per subtitle file

### Data Structures

**Input Data:**
- User URL (play or album format)
- Cookies (authentication)
- User preferences (language, format, season/episode filters)

**Intermediate Data:**
- Album metadata (title, year, type, regions)
- Episode list (for series)
- Video IDs (vid)
- DASH URLs with authentication
- Subtitle metadata

**Output Data:**
- Downloaded subtitle files (VTT/XML)
- Converted subtitle files (SRT/ASS)
- Organized directory structure

### Key Python Methods

**IQIYI Class Methods:**

1. **`main()`** - Entry point, routes to movie/series flow
2. **`movie_subtitle()`** - Process single video
3. **`series_subtitle()`** - Process multi-episode series
4. **`get_vid()`** - Extract video ID from play page
5. **`get_dash_url()`** - Generate authenticated DASH URL
6. **`get_auth_key()`** - Generate MD5-based auth key
7. **`get_subtitle()`** - Extract and filter subtitle URLs
8. **`download_subtitle()`** - Download and convert files

### Dependencies

**Python Libraries:**
- `orjson` - Fast JSON parsing
- `requests` - HTTP client
- `hashlib` - MD5 authentication
- `re` - Regex pattern matching
- `subprocess` - Node.js execution

**External Dependencies:**
- Node.js - Required for cmd5x.js
- cmd5x.js - iQIYI's vf parameter generation

**Configuration Files:**
- `user_config.toml` - Main configuration
- `configs/iQIYI.toml` - Service settings
- `cookies/www.iq.com_cookies.txt` - Authentication

### Error Handling

**Common Errors:**
1. Missing cookies → Re-export from browser
2. Expired cookies → Update cookie file
3. Invalid vf parameter → Check cookies and cmd5x.js
4. Region restriction → Use proxy
5. No subtitles → Video doesn't have embedded subtitles

**Error Detection:**
- HTTP status codes
- JSON response code field
- Presence of expected data fields
- Validation of extracted values

### Supported Features

**Content Types:**
- Movies (singleVideo)
- TV Series (longVideo)
- Multiple seasons
- Episode filtering

**Languages:**
- Chinese (Simplified/Traditional)
- English
- Japanese
- Korean
- Other supported languages

**Output Formats:**
- SRT (SubRip)
- ASS (Advanced SubStation)
- VTT (WebVTT original)

**Filtering Options:**
- By season
- By episode number
- By language
- Last episode only

## Usage Examples

### Basic Movie Download
```bash
python subtitle_downloader.py --service iqiyi \
  "https://www.iq.com/play/movie-abc123?lang=zh_tw"
```

### Series with Filters
```bash
python subtitle_downloader.py --service iqiyi \
  --season 1 \
  --episode 1,2,3 \
  --subtitle-language zh-Hans,en \
  --subtitle-format .srt \
  "https://www.iq.com/album/series-abc123"
```

### Debug Mode
```bash
python subtitle_downloader.py --service iqiyi \
  --log-level DEBUG \
  "https://www.iq.com/play/movie-abc123"
```

## Important Technical Details

### Authentication Flow
1. User exports cookies from browser
2. Cookies loaded into Python requests session
3. Each API call includes cookies in headers
4. DASH API requires additional authKey and vf parameters
5. authKey = MD5(salt + timestamp + tvid)
6. vf = cmd5x.js(DASH URL parameters)

### URL Transformations
1. User URL → Album URL (extract content_id)
2. Album URL → Play URL (for each episode)
3. Play URL → Video ID (scrape HTML)
4. Video ID → DASH URL (with authentication)
5. DASH URL → Subtitle URLs (parse JSON)
6. Relative paths → Absolute URLs (prepend domain)

### Rate Limiting
- 2-second delay between play page requests
- Prevents detection and blocking
- Respects server resources

### File Organization
```
downloads/
  Movie.Name.2023/
    Movie.Name.2023.zh_cn.srt
    Movie.Name.2023.en.srt
    zh_cn/
      Movie.Name.2023.zh_cn.vtt (original)
    en/
      Movie.Name.2023.en.vtt (original)

  Series.Name.S01/
    Series.Name.S01E01.zh_cn.srt
    Series.Name.S01E01.en.srt
    Series.Name.S01E02.zh_cn.srt
    ...
```

## Security Considerations

**Cookie Security:**
- Cookies contain authentication tokens
- Should be stored securely
- Expire over time
- Should not be shared

**API Security:**
- Timestamp-based validation prevents replay
- Device fingerprinting prevents unauthorized access
- Multi-layer authentication (cookies + authKey + vf)

**Responsible Use:**
- Respect rate limits
- Don't bypass authentication
- Don't share authenticated cookies
- Use only for personal use

## Future Improvements

**Potential Enhancements:**
1. Parallel episode processing
2. Caching for vid lookups
3. Automatic cookie refresh
4. Progress callbacks
5. Download history logging
6. Better error recovery
7. Support for more subtitle formats

**Maintenance:**
- Monitor for API changes
- Update cmd5x.js if needed
- Refresh cookie export instructions
- Add new language mappings

## Conclusion

This documentation provides a complete understanding of:
- How the iQIYI subtitle downloader works
- What APIs are called and what data is exchanged
- How authentication and security work
- How to use and troubleshoot the tool
- How to extend and modify the functionality

The system is well-architected with clear separation of concerns:
- BaseService handles common functionality
- IQIYI class implements service-specific logic
- Utils provide reusable helper functions
- Configuration is external and flexible

All aspects of the implementation are documented, from high-level architecture to low-level API details, making it easy to understand, use, and extend the functionality.

## Document Navigation

For specific information, refer to:

- **Quick start:** IQIYI-IMPLEMENTATION-GUIDE.md (Setup section)
- **How it works:** IQIYI-ARCHITECTURE.md (System Architecture)
- **API details:** IQIYI-API-REFERENCE.md (API Endpoints)
- **Step-by-step flow:** IQIYI-DATA-FLOW.md (Complete Data Flow)
- **Troubleshooting:** IQIYI-IMPLEMENTATION-GUIDE.md (Troubleshooting Guide)
- **Development:** IQIYI-IMPLEMENTATION-GUIDE.md (Development section)

All documentation is based on analysis of the actual implementation at:
`/Users/baagas0/Documents/project/subtitle-downloader/services/iqiyi/iqiyi.py`
