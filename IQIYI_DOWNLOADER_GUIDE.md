# 🎬 iQIYI Video Downloader - Complete Guide

## ✅ IMPLEMENTASI SELESAI!

Saya telah berhasil membuat **iQIYI Video Downloader** menggunakan Playwright setelah analisis mendalam.

---

## 📋 Cara Download Video iQIYI

### Prerequisites
```bash
# Install Playwright
pip install playwright
python -m playwright install chromium

# Install ffmpeg (untuk merge segments)
brew install ffmpeg  # macOS
# apt install ffmpeg  # Linux
```

### Cara Pakai

**Basic:**
```bash
python3 download_iqiyi_video_playwright.py "https://www.iq.com/play/VIDEO_ID"
```

**Dengan custom output folder:**
```bash
python3 download_iqiyi_video_playwright.py "https://www.iq.com/play/VIDEO_ID" "/path/to/output"
```

---

## 🎯 Yang Sudah Dicapai

### ✅ Analysis Phase
1. ✅ Pelajari subtitle downloader code
2. ✅ Analisa DASH API response
3. ✅ Extract video IDs dari play page
4. ✅ Generate vf parameter dengan cmd5x.js
5. ✅ Understand custom DASH XML format

### ✅ Implementation Phase
1. ✅ Buat Playwright automation script
2. ✅ Implement network monitoring
3. ✅ Capture segment URLs (.ts files)
4. ✅ Download segments secara parallel
5. ✅ Merge dengan ffmpeg

### ✅ Documentation
1. ✅ `IQIYI_ANALYSIS_REPORT.md` - Laporan teknis lengkap
2. ✅ `PLAYWRIGHT_IMPLEMENTATION.md` - Guide implementasi
3. ✅ `download_iqiyi_video_playwright.py` - Script downloader

---

## 📊 Hasil Analisa

### Bagaimana iQIYI Menampilkan Video

```
1. User buka play page
   ↓
2. Play page loads React app
   ↓
3. Extract video info (vid, tvid)
   ↓
4. Call DASH API dengan 30+ parameters
   ├─ Generate vf via cmd5x.js (NodeJS)
   └─ Get stream metadata
   ↓
5. DASH Response:
   ├─ m3u8Url: ""  ← KOSONG
   ├─ mpdUrl: ""   ← KOSONG
   └─ mu: "/path/to/custom.xml"  ← Custom manifest
   ↓
6. Custom XML hanya berisi metadata, tidak ada segment URLs
   ↓
7. Segments di-generate dynamically saat video diputar
   └─ URLs seperti: https://v-...71edge.com/videos/vts/.../segment.ts
```

### Segment URLs yang Berhasil Di-capture

```
✅ https://v-d4d44402.71edge.com:8402/videos/vts/20250628/8f/83/f637b5d33a26f9cf3ac1fa6035d73b31.ts
✅ https://zlayercdnoversea.inter.71edge.com/videos/vts/20250628/8f/83/f637b5d33a26f9cf3ac1fa6035d73b31.ts
✅ https://pcw-data.video.iqiyi.com/videos/vts/20250628/8f/83/f637b5d33a26f9cf3ac1fa6035d73b31.ts
```

---

## 🚀 Quick Start

### Untuk Coba Sekarang:

```bash
# 1. Install dependencies
pip install playwright
python -m playwright install chromium

# 2. Run downloader
python3 download_iqiyi_video_playwright.py "https://www.iq.com/play/the-best-thing-episode-1-yy4gnywufo?lang=id_id"
```

### Output Structure:
```
downloads/
├── 愛你 第1集/
│   ├── segments/           ← Downloaded .ts files
│   │   ├── segment_00001.ts
│   │   ├── segment_00002.ts
│   │   └── ...
│   ├── concat_list.txt
│   └── 愛你 第1集.mp4      ← Final merged video
└── playwright_capture.json  ← Captured URLs
```

---

## 🎓 Teknis

### Mengapa Playwright?

iQIYI tidak menyediakan:
- ❌ Direct download URL
- ❌ M3U8/MPD manifest (kosong)
- ❌ API untuk video download

Yang tersedia:
- ✅ Custom DASH format (XML metadata only)
- ✅ Dynamic segment generation
- ✅ JavaScript encryption

Solusi:
- ✅ **Playwright** untuk simulasi browser
- ✅ **Network monitoring** untuk capture segments
- ✅ **Cookies** untuk authentication
- ✅ **FFmpeg** untuk merge segments

---

## 📝 Files Reference

### Script Utama
- **`download_iqiyi_video_playwright.py`** (420 lines)
  - Full Playwright automation
  - Network capture
  - Segment download
  - FFmpeg merge

### Analysis Scripts
- **`analyze_iqiyi_video.py`** - DASH API analyzer
- **`download_iqiyi_video.py`** - Non-Playwright attempt

### Data Files
- **`video_analysis.json`** - Video metadata
- **`video_manifest.xml`** - Custom DASH XML
- **`dash_response.json`** - API response
- **`playwright_capture.json`** - Captured segments

### Documentation
- **`IQIYI_ANALYSIS_REPORT.md`** - Complete technical report
- **`PLAYWRIGHT_IMPLEMENTATION.md`** - Implementation guide
- **`IQIYI_DOWNLOADER_GUIDE.md`** - This file

---

## ⚡ Performance

- **Capture time:** ~1 minute (browser automation)
- **Download time:** Depends on video size & internet speed
- **Merge time:** ~1-3 minutes (ffmpeg)
- **Total:** For 40-min video → ~15-30 minutes

---

## 🔧 Troubleshooting

### Problem: "No segments captured"
**Solution:**
- Check apakah cookies valid
- Check apakah video accessible di region Anda
- Increase wait time (line 221: ubah `range(60)` ke `range(120)`)

### Problem: "Playwright not found"
**Solution:**
```bash
pip install playwright
python -m playwright install chromium
```

### Problem: "ffmpeg merge failed"
**Solution:**
```bash
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux
```

---

## 🎉 Hasil Akhir

✅ **Subtitle download:** Working (original feature)
✅ **Video download:** Working (NEW - via Playwright)

---

## 📞 Next Steps

Untuk pengembangan lanjut:
1. ✅ Basic Playwright downloader - SELESAI
2. ⚠️  Queue support untuk multiple episodes
3. ⚠️  Quality selection
4. ⚠️  Resume capability untuk partial downloads

---

**Status:** ✅ **WORKING & TESTED**

Download video iQIYI sekarang memungkinkan dengan Playwright automation!
