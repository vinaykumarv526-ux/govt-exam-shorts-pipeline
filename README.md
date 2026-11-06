# Autonomous Government Exam Shorts Pipeline 🇮🇳

An automated, production-ready pipeline that ingests daily Government Exam notifications, renders 1080x1920 (9:16 vertical) high-contrast short-form videos matching the **FreeJobAlert** layout, mixes royalty-free background music at -18dB, and schedules them to **YouTube Shorts** and **Facebook Reels**.

---

## 📸 Reference Layout Architecture (1080 × 1920)

```
+-------------------------------------------------------------+
| 1. Top Header (0-7%): Brand Logo & Header Bar               |
+------------------------------+------------------------------+
| 2. Split Visual Section (7-28%):                            |
|    Left (40%): Official      | Right (60%): Context-         |
|    Organization Emblem /     | relevant Profession Stock     |
|    Emblem Seal               | Scene Photo                   |
+------------------------------+------------------------------+
| 3. High-Impact Callout Banner (28-40%):                     |
|    - Heavy bold recruitment title (e.g. WBPSC SUB-SURVEYOR) |
|    - Extra-large Vacancy block (e.g. 1,145 POSTS)           |
|    - Highlights & eligibility chips                         |
+-------------------------------------------------------------+
| 4. Detailed Specification Table (40-90%):                   |
|    - Two-column bordered table with automatic line wrap     |
|    - Post Name, Vacancies, Qualification, Salary, Age Limit,|
|      Dates, Selection Process, Mode, Job Location           |
+-------------------------------------------------------------+
| 5. Bottom CTA & Progress Bar (90-100%):                     |
|    - High-visibility Yellow alert band                      |
|    - Animated timeline progress bar                         |
+-------------------------------------------------------------+
```

---

## 🎨 5 High-Contrast Rotating Color Palettes

Every newly generated video automatically rotates to the next color palette to keep your channel feed visually dynamic:

| Palette # | Theme Name | Header Bar | Title Color | Vacancy Banner | Table Labels |
|---|---|---|---|---|---|
| **1** | **Red & Navy** | `#0B3C5D` | `#D32F2F` | `#FFEB3B` (Yellow) | `#D32F2F` |
| **2** | **Green & Maroon** | `#1B5E20` | `#B71C1C` | `#FFEB3B` (Yellow) | `#1B5E20` |
| **3** | **Royal Blue & Orange**| `#1565C0` | `#E64A19` | `#FFF3E0` (Peach) | `#E64A19` |
| **4** | **Teal & Purple** | `#00796B` | `#6A1B9A` | `#FFECB3` (Amber) | `#00796B` |
| **5** | **Crimson & Slate** | `#263238` | `#C2185B` | `#E0F7FA` (Cyan) | `#C2185B` |

---

## 📂 Project Structure

```
govt exam posts/
├── assets/
│   ├── audio/                     # Background music loops (.wav / .mp3)
│   ├── branding/                  # FreeJobAlert / custom header banner
│   ├── emblems/                   # Official emblems (WBPSC, TNMVMD, NABFINS, ITPO, Central Govt)
│   └── stock_photos/              # Profession stock scenes (surveyor, mechanic, field officer, steno)
├── data/
│   ├── mock_exams.json            # Curated exam alerts matching reference screenshots
│   ├── pipeline_state.json        # Palette rotation and count persistence
│   └── scraped/                   # Cached scraped notifications
├── output/                        # Rendered MP4 videos, posters & audit logs
├── scraper.py                     # Data ingestion & recruitment portal scraper
├── renderer.py                    # 1080x1920 9:16 layout rendering & video engine
├── audio_mixer.py                 # Royalty-free music synthesizer & -18dB looper
├── scheduler.py                   # YouTube Shorts & Facebook Reels publisher
├── run_pipeline.py                # Master CLI orchestration runner
├── .env.example                   # API credentials template
└── requirements.txt               # Dependencies
```

---

## 🚀 Quick Start Guide

### 1. Run Pipeline with Pre-Packaged Mock Data (Instant Test)
```bash
python run_pipeline.py --source mock --limit 3 --duration 15 --fps 30
```

### 2. Fast Preview (Posters & Layout Check Only)
```bash
python run_pipeline.py --posters-only --limit 3
```

### 3. Live Scraping Mode
```bash
python run_pipeline.py --source live --limit 5 --duration 15
```

---

## 🔑 Publishing & Scheduling Setup

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### YouTube Data API v3:
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create an **OAuth 2.0 Client ID** (Desktop Application) and download the JSON file as `client_secrets.json` into the root directory.
4. On first upload, run `python scheduler.py` to authenticate in your browser and save `youtube_token.json`.

### Facebook Reels (Meta Graph API):
1. In [Meta for Developers](https://developers.facebook.com/), create an App with **Pages API**.
2. Generate a Page Access Token with `pages_manage_posts` and `pages_read_engagement`.
3. Add your `META_PAGE_ID` and `META_PAGE_ACCESS_TOKEN` into `.env`.

When running without API credentials or with default settings, the pipeline operates in **Safe Dry-Run / Simulation Mode**, ensuring all layout generation, video rendering, and metadata formatting are verified without failing.
