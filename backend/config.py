"""
AttentionX - Configuration
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Processing settings
MAX_VIDEO_SIZE_MB = 500
MAX_VIDEO_DURATION_SEC = 3600  # 1 hour
CLIP_MIN_DURATION = 15  # seconds
CLIP_MAX_DURATION = 60  # seconds
CLIP_TARGET_DURATION = 30  # seconds

# Virality scoring weights
VIRALITY_WEIGHTS = {
    "emotion_intensity": 0.25,
    "speech_energy": 0.20,
    "keyword_triggers": 0.20,
    "speech_rate_change": 0.15,
    "pitch_variation": 0.10,
    "content_novelty": 0.10,
}

# Trigger keywords that boost virality
VIRAL_KEYWORDS = [
    "secret", "mistake", "truth", "never", "always", "stop",
    "nobody", "everyone", "shocking", "actually", "exactly",
    "powerful", "dangerous", "incredible", "insane", "game-changer",
    "hack", "trick", "lesson", "failure", "success", "million",
    "first", "last", "only", "biggest", "worst", "best",
    "changed my life", "wish I knew", "don't do this",
    "here's why", "the real reason", "unpopular opinion",
    "hot take", "controversial", "mind-blowing", "revolutionary",
]

# Persona configurations
PERSONA_CONFIGS = {
    "students": {
        "tone": "casual, relatable, energetic",
        "vocabulary": "simple, modern slang okay, emoji-friendly",
        "focus": "learning, growth, exam tips, career prep",
        "hook_style": "curiosity-driven, FOMO-based",
    },
    "entrepreneurs": {
        "tone": "confident, action-oriented, inspiring",
        "vocabulary": "business terms, ROI-focused, strategic",
        "focus": "revenue, scaling, leadership, hustle",
        "hook_style": "results-driven, contrarian",
    },
    "developers": {
        "tone": "technical, precise, pragmatic",
        "vocabulary": "technical jargon welcome, code references",
        "focus": "efficiency, best practices, tools, architecture",
        "hook_style": "problem-solution, myth-busting",
    },
    "general": {
        "tone": "conversational, engaging, accessible",
        "vocabulary": "simple, clear, universal",
        "focus": "life improvement, practical advice",
        "hook_style": "story-based, emotional",
    },
    "marketers": {
        "tone": "data-driven, creative, trend-aware",
        "vocabulary": "marketing terms, metrics-focused",
        "focus": "growth, engagement, conversion, branding",
        "hook_style": "stat-leading, case-study",
    },
}

# Platform specifications
PLATFORM_SPECS = {
    "instagram_reel": {
        "max_duration": 90,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "max_caption_length": 2200,
        "hashtag_count": 15,
        "style": "visual, punchy, trend-aware",
    },
    "youtube_short": {
        "max_duration": 60,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "max_caption_length": 5000,
        "hashtag_count": 5,
        "style": "informative, searchable, value-packed",
    },
    "linkedin_post": {
        "max_duration": None,
        "aspect_ratio": None,
        "resolution": None,
        "max_caption_length": 3000,
        "hashtag_count": 5,
        "style": "professional, storytelling, thought-leadership",
    },
    "tiktok": {
        "max_duration": 60,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "max_caption_length": 300,
        "hashtag_count": 5,
        "style": "raw, authentic, hook-heavy",
    },
}
