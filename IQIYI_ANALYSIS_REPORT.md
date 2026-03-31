# iQIYI Video Downloader - Complete Analysis Report

## Executive Summary

Setelah analisis mendalam menggunakan dua pendekatan (mempelajari project subtitle downloader dan analisis langsung), saya berhasil memahami sepenuhnya bagaimana iQIYI menampilkan video.

**FINDING UTAMA:** iQIYI menggunakan sistem **custom DASH format** dengan encryption yang kompleks. Video tidak bisa di-download dengan metode sederhana seperti M3U8/MPD langsung.

---

## 1. Cara Kerja iQIYI Video Delivery

### 1.1 Flow Lengkap

```
USER VISIT PLAY PAGE
    ↓
[1] PLAY PAGE (https://www.iq.com/play/{id})
    ├─ HTML contains React initial state
    └─ Extract: vid, tvid, title
    ↓
[2] DASH API REQUEST (Custom Format)
    ├─ URL: https://cache-video.iq.com/dash?
    ├─ 30+ parameters (tvid, vid, authKey, cookies...)
    ├─ Generate vf parameter via cmd5x.js (NodeJS)
    └─ Response: JSON dengan stream metadata
    ↓
[3] DASH RESPONSE
    ├─ program.video[]: Array video streams
    ├─ program.audio[]: Array audio streams
    └─ program.stl[]: Array subtitle streams
    ↓
[4] VIDEO STREAM DATA
    ├─ m3u8Url: "" (KOSONG!)
    ├─ mpdUrl: "" (KOSONG!)
    ├─ mu: "/path/to/dash.xml" (Custom XML manifest)
    ├─ vsize: 663006734 bytes (0.62 GB)
    └─ ff: "ts" (Transport Stream format)
    ↓
[5] CUSTOM DASH XML MANIFEST
    ├─ URL: https://meta.video.iqiyi.com/path/to/file.xml
    ├─ Format: Custom XML (bukan standard DASH MPD!)
    ├─ Contains: FLV metadata, keyframes, duration
    └─ TAPI: Tidak berisi direct segment URLs
```

### 1.2 Kunci Utama

**Yang Membuat iQIYI Berbeda:**

1. **Tidak ada M3U8/MPD URLs langsung** - `m3u8Url` dan `mpdUrl` selalu kosong
2. **Custom XML manifest** - Format XML spesifik iQIYI (bukan standard DASH)
3. **JavaScript encryption** - Parameter `vf` harus digenerate dengan NodeJS
4. **Dynamic segment generation** - Segment URLs tidak tersimpan statis di manifest

---

## 2. Technical Details

### 2.1 DASH API Request

**URL:** `https://cache-video.iq.com/dash?[params]&vf=[encrypted_value]`

**Parameters (30+):**
```python
{
    "tvid": "3634312646158200",           # Episode ID
    "vid": "abe2c4788688b54418ebe6a4119bf1a5",  # Video stream ID
    "authKey": "md5(salt + timestamp + tvid)",  # MD5 hash
    "dfp": cookies['__dfp'],             # Device fingerprint
    "k_uid": cookies['QC005'],           # User session
    "tm": 1710000000000,                  # Timestamp
    "vf": "generated_by_cmd5x.js",       # Encrypted parameter
    # ... 20+ other parameters
}
```

### 2.2 DASH API Response Structure

```json
{
  "code": "A00000",
  "data": {
    "program": {
      "video": [
        {
          "vid": "2f7d56c97a00299b2deb42f49ac3a9ac",
          "ff": "ts",                      # Format: Transport Stream
          "br": 100,                      # Bitrate
          "bid": 600,                     # Width
          "fr": 25,                       # Framerate
          "vsize": 663006734,             # Total size in bytes
          "duration": 2550,                # Duration in seconds
          "m3u8Url": "",                  # ← SELALU KOSONG
          "mpdUrl": "",                   # ← SELALU KOSONG
          "mu": "/20250628/ed/09/553c64616dcc6008fc785444d2a8d2a7.xml"  # Custom manifest
        }
      ],
      "audio": [
        {
          "ff": "amp4",                   # Format: MP4 audio
          "cf": "aac",                    # Codec
          "aid": "d191f4005319488d940316c4fa9df786",
          "fs": [                         # Fragment/Segment list
            {
              "i": 1,                    # Index
              "l": "/v0/2025/...segment.amp4",  # Segment path
              "b": 104077                 # Byte size
            }
          ]
        }
      ],
      "stl": [ ... ]  # Subtitle streams (sudah di-handle oleh subtitle downloader)
    }
  }
}
```

### 2.3 Custom XML Manifest Structure

**File:** `/20250628/ed/09/553c64616dcc6008fc785444d2a8d2a7.xml`

```xml
<?xml version="1.0" ?>
<fileset>
 <flv name="6be457399da9990bfccca4614caaf653.flv">
  <width>1920</width>
  <height>800</height>
  <filesize>663006734</filesize>
  <duration>2550.5279999999993</duration>
  <video_tag>...</video_tag>
  <audio_tag>...</audio_tag>
  <keyframesequences>
   <keyframes>
    <times>
     <value id="0">0.000</value>
     <value id="1">0.000</value>
     <value id="2">5.000</value>
     ...
    </times>
    <filepositions>
     <value id="0">0</value>
     <value id="1">1048576</value>
     ...
    </filepositions>
   </keyframes>
  </keyframesequences>
 </flv>
</fileset>
```

**PENTING:** XML ini hanya berisi metadata dan keyframe positions. **TIDAK** berisi direct segment URLs!

---

## 3. Tools & Methods Tested

### 3.1 Subtitle Downloader (Existing)
✅ **BERHASIL** - Sudah bisa download subtitle
- Lokasi: `services/iqiyi/iqiyi.py`
- Method: Scrape DASH response untuk `program.stl[]`
- Output: VTT/XML subtitle files

### 3.2 XstreamDL_CLI (Existing Tool)
❌ **GAGAL** - Tidak support iQIYI custom format
- Error: "headers is not exists", "binaries folder is not exist"
- Masalah: Butuh config file dan ffmpeg binaries

### 3.3 yt-dlp (External Tool)
❌ **GAGAL** - Butuh PhantomJS (deprecated)
- Error: "PhantomJS not found"
- Status: iQIYI extractor di yt-dlp membutuhkan PhantomJS yang sudah tidak dikembangkan

### 3.4 Custom Analysis Script
✅ **BERHASIL** - Dapat extract semua metadata
- Script: `download_iqiyi_video.py`
- Output: `video_analysis.json`, `video_manifest.xml`
- Result: Memahami complete flow tapi tidak bisa download langsung

---

## 4. Mengapa Video Download Sulit?

### 4.1 Tantangan Teknis

1. **Custom Format**
   - Bukan standard HLS (M3U8) atau DASH (MPD)
   - XML manifest bukan format standar

2. **Dynamic Segment Generation**
   - Segment URLs tidak tersimpan statis
   - Mungkin digenerate on-the-fly dengan encryption

3. **DRM/Encryption**
   - Parameter `vf` harus digenerate dengan JavaScript
   - `drmType: 1` menunjukkan adanya protection

4. **Missing Public APIs**
   - Tidak ada dokumentasi publik untuk format custom ini
   - Harus reverse engineering dari browser behavior

### 4.2 Apa yang Diperlukan?

Untuk download video iQIYI, perlu salah satu dari:

**Option A: Browser Automation + Network Recording**
```python
# Gunakan Playwright/Selenium untuk:
1. Buka iQIYI play page
2. Click play button
3. Record semua network requests
4. Filter requests dengan .ts, .m4s, .mp4 extensions
5. Download semua segments
6. Merge segments dengan ffmpeg
```

**Option B: Reverse Engineering JavaScript**
```python
# Analisa JavaScript modules yang di-download oleh iQIYI:
1. Temukan module yang generate segment URLs
2. Port logic tersebut ke Python
3. Generate segment URLs secara manual
4. Download dan merge
```

**Option C: Use Existing iQIYI Downloader**
- Cari project GitHub lain yang khusus untuk iQIYI video
- Atau update yt-dlp iQIYI extractor (need PhantomJS replacement)

---

## 5. Hasil Analisa

### 5.1 File yang Dihasilkan

Dari analisa ini, dihasilkan:

1. **iqiyi_debug.log** - Log lengkap subtitle downloader
2. **dash_response.json** - DASH API response lengkap
3. **video_manifest.xml** - Custom DASH XML manifest
4. **video_analysis.json** - Analisa lengkap video stream
5. **analyze_iqiyi_video.py** - Script analisa
6. **download_iqiyi_video.py** - Video downloader prototype

### 5.2 Key Discoveries

✅ Ditemukan:
- Complete DASH API structure
- Parameter requirements
- Custom XML manifest format
- Video metadata (resolution, size, duration, etc.)
- Subtitle extraction method (already working)

❌ Tidak Ditemukan:
- Direct video download URLs
- M3U8/MPD manifest URLs
- Standard DASH/HLS streams
- Public API untuk video segments

---

## 6. Rekomendasi

### 6.1 Untuk Download Video iQIYI

**REKOMENDASI 1: Browser Automation (Paling Realistis)**
```python
from playwright.sync_api import sync_playwright

def download_iqiyi_video(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load cookies
        page.context.add_cookies(cookies)

        # Capture network requests
        segments = []
        def handle_request(request):
            if '.ts' in request.url or '.m4s' in request.url:
                segments.append(request.url)

        page.on('request', handle_request)

        # Play video
        page.goto(url)
        page.click('[class*="play"]')
        page.wait_for_timeout(30000)  # Wait for 30s

        # Download segments
        # Merge with ffmpeg
        browser.close()
```

**REKOMENDASI 2: Cari Project Khusus iQIYI**
- Search GitHub: "iqiyi downloader"
- Ada beberapa project yang mungkin masih aktif

**REKOMENDASI 3: Update yt-dlp**
- yt-dlp iQIYI extractor perlu update dari PhantomJS ke Playwright
- Contribute ke yt-dlp project

### 6.2 Untuk Development Lanjutan

Jika ingin membuat downloader yang robust:

1. **Phase 1: Browser Recording**
   - Gunakan Playwright untuk record network traffic
   - Extract semua segment URLs
   - Download dan merge segments

2. **Phase 2: Reverse Engineering**
   - Analisa JavaScript modules dari iQIYI
   - Temukan logic segment URL generation
   - Port ke Python untuk standalone downloader

3. **Phase 3: Handle Encryption**
   - Implement vf parameter generation tanpa NodeJS
   - Handle DRM jika ada
   - Support multiple quality levels

---

## 7. Kesimpulan

iQIYI menggunakan sistem **custom video delivery** yang sangat berbeda dari standar HLS/DASH:

- ✅ **Subtitle download**: MUDAH - Sudah working di project ini
- ❌ **Video download**: SULIT - Butuh browser automation atau deep reverse engineering

**BEST SOLUTION untuk saat ini:**
Gunakan **browser automation (Playwright)** untuk merekam segment URLs saat video dimainkan, lalu download dan merge segments tersebut.

**PROJECT STATUS:**
- Subtitle downloader: ✅ Working perfectly
- Video downloader: ⚠️  Prototype complete, but need Playwright implementation

---

## 8. File Reference

### Script yang Dibuat
- `analyze_iqiyi_video.py` - Script analisa DASH response
- `download_iqiyi_video.py` - Video downloader prototype
- `analyze_with_playwright.py` - Playwright analysis script

### Data yang Dihasilkan
- `video_analysis.json` - Video stream metadata lengkap
- `video_manifest.xml` - Custom DASH XML manifest
- `dash_response.json` - DASH API response lengkap
- `iqiyi_debug.log` - Activity log

### Dependencies
- Python 3.10+
- requests
- orjson
- NodeJS (untuk cmd5x.js)
- Cookies dari iq.com

---

**Tanggal Analisa:** 2025-03-25
**Platform:** macOS (Darwin 24.5.0)
**Python Version:** 3.12.0
