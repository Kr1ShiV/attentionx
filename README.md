# ⚡ AttentionX — AI Content Intelligence Engine

<div align="center">

![AttentionX Banner](https://img.shields.io/badge/AttentionX-AI%20Content%20Intelligence-7c3aed?style=for-the-badge&logo=lightning&logoColor=white)

**Transform long-form videos into viral-ready short-form content with AI-powered analysis**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-4285F4?style=flat-square&logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Live Demo](https://attentionx.onrender.com) • [Features](#features) • [Tech Stack](#tech-stack) • [Quick Start](#quick-start) • [Architecture](#architecture)

</div>

---

### 🌐 Live Deployment
> **Try the fully functional app here:** **[https://attentionx.onrender.com](https://attentionx.onrender.com)**  
> *(No local installation required. Evaluators can instantly test the AI video processing, virality heatmaps, and hook generation engine).*

---

## 🎬 Demo Video

> 📹 **[Watch the 2-Minute Demo Video Here](https://drive.google.com/file/d/17wous95IKcjrc6b8XGlvh9ZjAPhRy4Z1/view?usp=sharing)**

### 5-Minute Demo Script

1. **[0:00-0:30] Intro** — Show the problem, introduce AttentionX
2. **[0:30-1:30] Upload & Processing** — Upload a video, show the AI pipeline  
3. **[1:30-2:30] Dashboard** — Attention heatmap, virality scores, audio analysis
4. **[2:30-3:30] Clips & Hooks** — Browse segments, generate hooks in different styles
5. **[3:30-4:30] Remix Mode** — Persona adapter + platform optimization for all 4 platforms
6. **[4:30-5:00] Story Builder** — Combine clips into narrative, export

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

## <a id="features"></a>🚀 Features

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

---

## <a id="tech-stack"></a>🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **Node.js & Express** | High-performance server and API handler |
| **FFmpeg / ffprobe** | Video duration extraction & audio processing |
| **Multer** | Robust file upload handling |

### AI Layer
| Technology | Purpose |
|-----------|---------|
| **Google Gemini 2.5 Flash** | Audio transcription, hook generation, persona adaptation, virality analysis, and story building |
| **@google/generative-ai** | Official Google AI SDK for Node.js |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Vanilla JS** | Zero-dependency, fast loading |
| **Canvas API** | Custom heatmap & waveform visualizations |
| **CSS3** | Glassmorphism, animations, responsive design, SVG platform icons |

---

## <a id="quick-start"></a>🚀 Quick Start

### Prerequisites
- Node.js (v18+)
- FFmpeg installed and added to system PATH
- Google Gemini API Key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Kr1ShiV/attentionx.git
cd attentionx

# 2. Install dependencies
npm install

# 3. Set API key
# On Windows:
set GEMINI_API_KEY=your_gemini_api_key
# On Mac/Linux:
export GEMINI_API_KEY="your_gemini_api_key"

# 4. Start the server
node server.js
```

### Access the App
Open your browser: **http://localhost:3000**

### Try Without Upload
Click **"🎮 Try Demo"** button to load sample data and explore all features immediately without using API quotas.

---

## 📁 Project Structure

```
attentionx/
├── server.js                    # Express app, Gemini AI logic, FFmpeg processing
├── package.json                 # Node.js dependencies
├── frontend/
│   ├── index.html               # Main dashboard UI
│   ├── css/styles.css           # Premium dark theme
│   └── js/
│       ├── app.js               # Core application logic
│       ├── api.js               # API client
│       └── visualizations.js    # Canvas heatmap & waveform
├── uploads/                     # Temp storage for uploaded video files
├── README.md
└── DEMO_FLOW.md                 # Demo presentation script
```

---

## <a id="architecture"></a>🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Frontend (HTML/CSS/JS)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Upload   │ │Dashboard │ │  Clips   │ │  Remix Mode   │  │
│  │ Zone     │ │ Heatmap  │ │  Grid    │ │ (IG, YT, IN)  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬───────┘  │
│       │             │            │              │          │
└───────┼─────────────┼────────────┼──────────────┼──────────┘
        │             │            │              │
        ▼             ▼            ▼              ▼
┌────────────────── Node.js / Express Server ─────────────────┐
│                                                             │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │  Multer  │  │ FFmpeg System │  │ Gemini API SDK       │  │
│  │ (Upload) │  │ (Duration/Audio)││ (gemini-2.5-flash)   │  │
│  └────┬─────┘  └───────┬───────┘  └──────────┬───────────┘  │
│       │                │                     │              │
│       ▼                ▼                     ▼              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            AttentionX AI Orchestration                │  │
│  │  - Video processing & audio extraction                │  │
│  │  - Prompt engineering & fallback logic                │  │
│  │  - Virality scoring (0-100) based on transcript       │  │
│  │  - Persona adaptation & Story Arc building            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
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

Built for the **AttentionX AI Hackathon**.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

<div align="center">

**Built for the AttentionX Hackathon**

⚡ **AttentionX** — *Turn Hours Into Viral Moments*

</div>
