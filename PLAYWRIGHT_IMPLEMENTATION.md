# iQIYI Video Downloader - Playwright Implementation

## Overview

Berikut adalah implementasi lengkap **iQIYI Video Downloader menggunakan Playwright**. Ini adalah solusi yang berhasil men-download video dari iQIYI setelah analisis mendalam.

## 📁 Files yang Dibuat

### 1. `download_iqiyi_video_playwright.py`
Script utama untuk download video iQIYI menggunakan Playwright automation.

**Fitur:**
- ✅ Ekstrak video info dari play page
- ✅ Launch browser dengan Playwright (Chromium)
- ✅ Load cookies dari file
- ✅ Monitor network traffic saat video diputar
- ✅ Capture semua segment URLs (.ts files)
- ✅ Download semua segments secara parallel
- ✅ Merge segments dengan ffmpeg menjadi MP4

## 🚀 Cara Penggunaan

### Prerequisites

```bash
# 1. Install Python dependencies
pip install playwright requests

# 2. Install Chromium browser untuk Playwright
python -m playwright install chromium

# 3. Install ffmpeg (untuk merge segments)
brew install ffmpeg  # macOS
# atau
apt install ffmpeg  # Linux
```

### Basic Usage

```bash
# Download video (all quality, all segments)
python3 download_iqiyi_video_playwright.py "https://www.iq.com/play/VIDEO_ID"

# Download ke custom directory
python3 download_iqiyi_video_playwright.py "https://www.iq.com/play/VIDEO_ID" "/path/to/output"
```

### Output Structure

```
downloads/
├── {Video Title}/
│   ├── segments/
│   │   ├── segment_00001.ts
│   │   ├── segment_00002.ts
│   │   ├── ...
│   │   └── segment_00XXX.ts
│   ├── concat_list.txt
│   └── {Video Title}.mp4  ← Final merged video
├── playwright_capture.json  ← Captured segment URLs
└── manifest.m3u8  ← (if found)
```

## 🔧 Cara Kerja

### Phase 1: Video Info Extraction
```python
# Parse play page HTML
# Extract React props
# Get: title, duration, album info
```

### Phase 2: Browser Automation
```python
# Launch Chromium browser
# Load cookies from cookies/www.iq.com_cookies.txt
# Navigate to play page
# Click play button
```

### Phase 3: Network Monitoring
```python
# Monitor semua network requests
# Filter requests dengan .ts, .m4s extensions
# Capture semua segment URLs
# Wait 60 seconds untuk collect semua segments
```

### Phase 4: Download Segments
```python
# Download setiap segment secara parallel
# Save ke segments/ folder
# Retry jika gagal
```

### Phase 5: Merge dengan FFmpeg
```python
# Create concat list file
# Run ffmpeg untuk merge semua .ts files
# Output: {Video Title}.mp4
```

## 📊 Script Flow

```
START
  ↓
[1] Extract video info from URL
  ├─ Parse HTML
  └─ Get title, duration, etc.
  ↓
[2] Launch Playwright browser
  ├─ Load cookies
  └─ Setup network monitoring
  ↓
[3] Navigate to play page
  ├─ Load page (domcontentloaded)
  └─ Wait for player to load
  ↓
[4] Click play button
  ├─ Try various selectors
  └─ Fallback: click video container
  ↓
[5] Monitor network traffic (60 seconds)
  ├─ Capture .ts/.m4s URLs
  ├─ Capture .m3u8/.mpd URLs
  └─ Save to playwright_capture.json
  ↓
[6] Download segments
  ├─ Deduplicate URLs
  ├─ Download each segment
  └─ Save to segments/ folder
  ↓
[7] Merge with ffmpeg
  ├─ Create concat list
  ├─ Run ffmpeg merge
  └─ Output: video.mp4
  ↓
DONE
```

## 🎯 Key Features

### 1. Network Request Capture
```python
def log_request(request):
    url = request.url
    if '.ts' in url or '.m4s' in url:
        segment_urls.append(url)
```

### 2. Cookie Handling
```python
# Load dari cookies/www.iq.com_cookies.txt
# Convert ke Playwright format
# Set ke browser context
```

### 3. Auto-Play Detection
```python
# Try multiple selectors for play button
# Fallback strategies
# Handle various iQIYI player versions
```

### 4. Segment Deduplication
```python
unique_segments = list(dict.fromkeys(segment_urls))
# Remove duplicates while preserving order
```

### 5. FFmpeg Integration
```python
# Create concat list
# Merge with copy codec (fast, no re-encode)
# Fix AAC format
```

## 🐛 Troubleshooting

### Error: "Playwright not found"
**Solution:**
```bash
pip install playwright
python -m playwright install chromium
```

### Error: "ffmpeg not found"
**Solution:**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Tidak ada segments yang ter-capture
**Possible causes:**
1. Cookies expired → Renew cookies dari browser
2. Video requires VIP → Login dengan premium account
3. Geo-blocking → Gunakan proxy dari region yang diizinkan
4. Play button tidak ter-click → Script akan lanjut dengan fallback

### Segments tidak ter-download semua
**Solution:**
- Check `playwright_capture.json` untuk melihat berapa yang ter-capture
- Increase wait time di script (line 221: ubah `range(60)` ke `range(120)`)
- Check network connection

## 📈 Performance

### Estimated Time

| Video Duration | Capture Time | Download Time | Merge Time |
|----------------|--------------|---------------|------------|
| 20 min | 1 min | 5-10 min | 1-2 min |
| 40 min | 1 min | 10-20 min | 2-3 min |
| 60 min | 1 min | 15-30 min | 3-5 min |

### Resource Usage

- **RAM:** ~500MB (Chromium) + ~100MB (Python)
- **Disk:** Temporary = 2x video size, Final = 1x video size
- **Network:** Full video bandwidth

## 🔐 Security & Privacy

### Cookies
- Dibaca dari `cookies/www.iq.com_cookies.txt`
- Hanya dikirim ke iq.com domain
- Tidak disimpan ke tempat lain

### Network Traffic
- Semua request melalui cookies authentication
- Tidak ada data yang dikirim ke pihak ketiga
- Browser ditutup setelah selesai

## 🎓 Advanced Usage

### Custom Wait Time
Edit script line 221:
```python
# Default: 60 seconds
for i in range(60):  # Ubah ke 120 untuk video lebih panjang
```

### Headless Mode
Edit script line 182:
```python
browser = p.chromium.launch(
    headless=True,  # ← Ubah ke True
    args=[...]
)
```

### Download Specific Quality
Script akan capture semua available segments. Untuk filter quality:
1. Check `playwright_capture.json`
2. Filter URLs by quality indicator (biasanya di URL path)
3. Modify script untuk filter sebelum download

### Rate Limiting
Add delay antar segments:
```python
import time
time.sleep(0.5)  # 500ms delay antar requests
```

## 📝 Contoh Segment URLs yang Di-capture

```
https://v-d4d44402.71edge.com:8402/videos/vts/20250628/8f/83/f637b5d33a26f9cf3ac1fa6035d73b31.ts?key=...
https://zlayercdnoversea.inter.71edge.com/videos/vts/20250628/8f/83/f637b5d33a26f9cf3ac1fa6035d73b31.ts?start=...
https://pcw-data.video.iqiyi.com/videos/vts/20250628/8f/83/f637b5d33a26f9cf3ac1fa6035d73b31.ts?qd_tvid=...
```

**Pattern:**
- CDN: `71edge.com`, `inter.71edge.com`, `video.iqiyi.com`
- Path: `/videos/vts/YYYY/MM/DD/...`
- Format: `.ts` (Transport Stream)
- Parameters: `key`, `start`, `qd_tvid`, etc.

## 🔄 Alternative: Direct Segment Download

Jika Anda sudah punya list segment URLs, bisa download langsung:

```python
import requests
from urllib.parse import urlparse
import os

urls = [
    "https://v-d4d44402.71edge.com:8402/videos/...segment1.ts",
    "https://v-d4d44402.71edge.com:8402/videos/...segment2.ts",
    # ... more URLs
]

session = requests.Session()
# Load cookies...

for i, url in enumerate(urls):
    filename = f"segment_{i:05d}.ts"
    # Extract filename dari URL jika ada
    parsed = urlparse(url)
    url_filename = os.path.basename(parsed.path)
    if url_filename and len(url_filename) > 5:
        filename = url_filename

    resp = session.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded: {filename}")
```

## 🆚 Comparison: Methods

| Method | Pros | Cons |
|--------|------|------|
| **Playwright (This)** | ✅ Works! Reliable | ⚠️ Slow (needs full browser) |
| **yt-dlp** | ✅ Fast | ❌ Requires PhantomJS (deprecated) |
| **XstreamDL_CLI** | ✅ Good for standard HLS/DASH | ❌ Doesn't support iQIYI custom format |
| **Manual Browser DevTools** | ✅ Works, free | ❌ Tedious, manual process |

## 💡 Tips

1. **First Time Setup** - Pastikan Playwright dan Chromium terinstall
2. **Cookies Fresh** - Renew cookies jika expired
3. **Stable Connection** - Video segments butuh stable internet
4. **Disk Space** - Sediakan 2x ruang dari ukuran video
5. **Testing** - Test dengan video pendek dulu

## 📞 Support

Jika ada issues:
1. Check `playwright_download.log` untuk error details
2. Check `playwright_capture.json` untuk melihat apa yang ter-capture
3. Run dengan debug mode untuk melihat lebih detail

## 🎉 Success Criteria

✅ **Successful download jika:**
- `playwright_capture.json` berisi segment URLs
- `segments/` folder berisi .ts files
- `{Video Title}.mp4` file ter-create
- Video bisa dimainkan dengan VLC/mpv

## 📚 Related Files

- `IQIYI_ANALYSIS_REPORT.md` - Complete technical analysis
- `download_iqiyi_video.py` - Non-Playwright analysis script
- `video_analysis.json` - Video metadata from DASH API
- `video_manifest.xml` - Custom DASH XML manifest

---

**Created:** 2025-03-25
**Status:** ✅ Working - Tested with iQIYI videos
**License:** Same as parent project (NON-COMMERCIAL USE ONLY)
