# ⚡ AttentionX — AI Content Intelligence Engine

<div align="center">

![AttentionX Banner](https://img.shields.io/badge/AttentionX-AI%20Content%20Intelligence-7c3aed?style=for-the-badge&logo=lightning&logoColor=white)

**Transform long-form videos into viral-ready short-form content with AI-powered analysis**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-4285F4?style=flat-square&logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Live Demo](#demo) • [Features](#-features) • [Tech Stack](#-tech-stack) • [Quick Start](#-quick-start) • [Architecture](#-architecture)

</div>

---

## 🎯 Problem Statement

Mentors, educators, and creators produce hours of high-value, long-form video content. However, modern audiences consume content in **60-second bursts**. Valuable "golden nuggets" of wisdom are often buried in 60-minute videos, making them inaccessible.

**Common challenges:**
- 🔍 Sifting through hours of footage to find viral moments manually
- 📐 Converting horizontal (16:9) to vertical (9:16) while keeping the speaker centered
- ✍️ Manually crafting hooks and captions for each platform
- 🎯 No data-driven way to predict which clips will perform best

## 💡 Solution

**AttentionX** is an AI-powered Content Intelligence Engine that doesn't just clip videos — it **predicts virality, generates hooks, adapts for audiences, and optimizes for every platform**.

---

## 🚀 Features

### Core Engine
| Feature | Description | Status |
|---------|-------------|--------|
| 📤 Video Upload | Drag & drop video upload with progress tracking | ✅ |
| 🗣️ Transcription | AI speech-to-text with timestamps (Whisper + Gemini) | ✅ |
| 🎵 Audio Analysis | Energy, pitch, speech rate analysis via Librosa | ✅ |
| ✂️ Smart Clipping | Automatic segment detection with MoviePy | ✅ |

### 🧠 Viral Moment Prediction Engine
Predicts which segments are likely to go viral **BEFORE** clipping using:
- **Emotion detection** (text sentiment + voice patterns)
- **Speech intensity** (pitch, speed, energy)
- **Keyword triggers** (e.g., "secret", "mistake", "truth")
- **Output:** Virality Score (0–100)

### 👀 Attention Heatmap Timeline
Interactive visual timeline showing:
- 🔴 High engagement zones (viral gold)
- 🔵 Drop-off zones  
- Helps understand *why* a clip is chosen

### 🎬 Hook Generator Engine
Automatically generates 3 viral hooks per clip using:
- **5 hook styles:** Curiosity, Shock, Challenge, Story, Value
- **Pattern-based hooks:** "Nobody tells you this about…", "This mistake cost me…"
- **AI-powered:** Custom hooks via Gemini API

### 🎯 Audience Persona Adapter
Select your target audience and AI rewrites everything:
- 🎓 **Students** — Casual, relatable, energetic
- 💼 **Entrepreneurs** — Action-oriented, ROI-focused
- 💻 **Developers** — Technical, precise, pragmatic
- 📊 **Marketers** — Data-driven, growth-focused
- 🌐 **General** — Universal, accessible

### 🧩 Auto Story Builder
Combine multiple clips into narrative flows:
- **Problem → Insight → Solution**
- **Hook → Build → Payoff**
- **Before → After**
- **Myth → Reality**

### 🔥 Content Remix Mode (KILLER FEATURE)
Convert the same clip into platform-optimized formats:
- 📸 **Instagram Reel** — Visual, punchy, trend-aware + 15 hashtags
- ▶️ **YouTube Short** — Informative, searchable, value-packed
- 💼 **LinkedIn Post** — Professional text-based storytelling
- 🎵 **TikTok** — Raw, authentic, hook-heavy

### 📱 Smart Vertical Framing
- Face tracking via MediaPipe
- Dynamic speaker centering for 9:16 crops
- Smooth frame transitions (no jitter)

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | High-performance Python API framework |
| **OpenAI Whisper** | Industry-standard speech-to-text |
| **Librosa** | Audio feature extraction & analysis |
| **MoviePy** | Video editing & clip extraction |
| **MediaPipe** | Face detection & tracking |

### AI Layer
| Technology | Purpose |
|-----------|---------|
| **Google Gemini 2.0** | Hook generation, persona adaptation, virality analysis |
| **NLP Pipeline** | Keyword detection, sentiment analysis, emotion scoring |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Vanilla JS** | Zero-dependency, fast loading |
| **Canvas API** | Custom heatmap & waveform visualizations |
| **CSS3** | Glassmorphism, animations, responsive design |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- FFmpeg (for audio extraction)
- Google Gemini API Key (optional, for AI features)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/attentionx.git
cd attentionx

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Set API key (optional)
export GEMINI_API_KEY="your-api-key-here"
# On Windows: set GEMINI_API_KEY=your-api-key-here

# 5. Run the server
python main.py
```

### Access the App
Open your browser: **http://localhost:8000**

### Try Without Upload
Click **"🎮 Try Demo"** button to load sample data and explore all features immediately.

---

## 📁 Project Structure

```
attentionx/
├── backend/
│   ├── main.py                  # FastAPI app with all endpoints
│   ├── config.py                # Configuration & scoring weights
│   ├── requirements.txt         # Python dependencies
│   ├── services/
│   │   ├── transcription.py     # Whisper/Gemini speech-to-text
│   │   ├── audio_analyzer.py    # Librosa audio feature extraction
│   │   ├── virality_engine.py   # Multi-signal virality prediction
│   │   ├── hook_generator.py    # AI + pattern-based hook generation
│   │   ├── persona_adapter.py   # Audience persona content rewriting
│   │   ├── clip_extractor.py    # Video clipping with MoviePy
│   │   ├── story_builder.py     # Narrative arc builder
│   │   ├── remix_engine.py      # Multi-platform content optimizer
│   │   └── face_tracker.py      # MediaPipe face tracking
│   └── models/
│       └── schemas.py           # Pydantic data models
├── frontend/
│   ├── index.html               # Main dashboard UI
│   ├── css/styles.css           # Premium dark theme
│   └── js/
│       ├── app.js               # Core application logic
│       ├── api.js               # API client
│       └── visualizations.js    # Canvas heatmap & waveform
├── uploads/                     # Uploaded video files
├── outputs/                     # Processed clips
├── README.md
└── DEMO_FLOW.md                 # Demo presentation script
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Upload   │ │Dashboard │ │  Clips   │ │   Remix   │  │
│  │ Zone     │ │ Heatmap  │ │  Grid    │ │   Mode    │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
│       │             │            │              │        │
└───────┼─────────────┼────────────┼──────────────┼────────┘
        │             │            │              │
        ▼             ▼            ▼              ▼
┌─────────────────── FastAPI Backend ──────────────────────┐
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Transcribe│  │  Audio   │  │  Face    │              │
│  │(Whisper) │  │ Analyzer │  │ Tracker  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │             │                     │
│       ▼              ▼             ▼                     │
│  ┌──────────────────────────────────────┐               │
│  │      Virality Prediction Engine      │               │
│  │  (Emotion + Energy + Keywords +      │               │
│  │   Speech Rate + Pitch + Novelty)     │               │
│  └───────────────┬──────────────────────┘               │
│                  │                                       │
│     ┌────────────┼────────────┐                         │
│     ▼            ▼            ▼                         │
│  ┌──────┐  ┌──────────┐  ┌───────┐                     │
│  │Hooks │  │ Persona  │  │ Remix │                     │
│  │Engine│  │ Adapter  │  │Engine │                     │
│  └──────┘  └──────────┘  └───────┘                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐                             │
│  │  Story   │  │  Clip    │                             │
│  │ Builder  │  │Extractor │                             │
│  └──────────┘  └──────────┘                             │
│                                                          │
└─────────────────── Gemini AI API ────────────────────────┘
```

---

## 📊 Virality Scoring Algorithm

The **Viral Moment Prediction Engine** uses a weighted multi-signal approach:

| Signal | Weight | How It Works |
|--------|--------|-------------|
| Emotion Intensity | 25% | Text sentiment + exclamation density + sentence variety |
| Speech Energy | 20% | RMS energy peaks from audio analysis |
| Keyword Triggers | 20% | Detection of 40+ viral power words |
| Speech Rate Change | 15% | Pacing variation (dynamic = engaging) |
| Pitch Variation | 10% | Voice pitch changes signal passion |
| Content Novelty | 10% | Contrarian/unique statements score higher |

**Formula:** `Virality Score = Σ(weight_i × signal_i) × 100`

---

## 🎬 Demo Video

> 📹 [Watch the Demo Video](#) <!-- Add Google Drive link here -->

### 5-Minute Demo Script

1. **[0:00-0:30] Intro** — Show the problem, introduce AttentionX
2. **[0:30-1:30] Upload & Processing** — Upload a video, show the AI pipeline  
3. **[1:30-2:30] Dashboard** — Attention heatmap, virality scores, audio analysis
4. **[2:30-3:30] Clips & Hooks** — Browse segments, generate hooks in different styles
5. **[3:30-4:30] Remix Mode** — Persona adapter + platform optimization for all 4 platforms
6. **[4:30-5:00] Story Builder** — Combine clips into narrative, export

---

## 🏆 Why AttentionX Stands Out

| Criteria | How We Excel |
|----------|-------------|
| **Innovation** | Virality Prediction Engine + Auto Story Builder — truly unique features |
| **UX** | Premium dark dashboard with glassmorphism, interactive heatmap, one-click everything |
| **Impact** | Solves real problem for 50M+ creators, educators, podcasters |
| **Technical** | Multi-signal ML pipeline, 7 AI services, real-time processing |
| **Demo WOW** | Instant demo mode, beautiful visualizations, smooth animations |

---

## 🔮 Future Roadmap

- [ ] Real-time video processing (streaming)
- [ ] A/B testing for hooks (track engagement)
- [ ] Chrome extension for YouTube
- [ ] Team collaboration features
- [ ] Auto-publish to social platforms
- [ ] Batch processing (multiple videos)

---

## 👥 Team

Built for the **AttentionX AI Hackathon** by UnsaidTalks.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

<div align="center">

**Built with ❤️ and AI for the AttentionX Hackathon**

⚡ **AttentionX** — *Turn Hours Into Viral Moments*

</div>
