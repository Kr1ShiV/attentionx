"""
AttentionX - Pydantic Models & Schemas
Defines all data models for the API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    ANALYZING_AUDIO = "analyzing_audio"
    DETECTING_FACES = "detecting_faces"
    SCORING_VIRALITY = "scoring_virality"
    GENERATING_CLIPS = "generating_clips"
    COMPLETED = "completed"
    FAILED = "failed"


class DeviceType(str, Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"


class Platform(str, Enum):
    INSTAGRAM_REEL = "instagram_reel"
    YOUTUBE_SHORT = "youtube_short"
    LINKEDIN_POST = "linkedin_post"
    TIKTOK = "tiktok"


class Persona(str, Enum):
    STUDENTS = "students"
    ENTREPRENEURS = "entrepreneurs"
    DEVELOPERS = "developers"
    GENERAL = "general"
    MARKETERS = "marketers"


class TranscriptSegment(BaseModel):
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


class EmotionData(BaseModel):
    joy: float = Field(default=0.0, ge=0.0, le=1.0)
    surprise: float = Field(default=0.0, ge=0.0, le=1.0)
    anger: float = Field(default=0.0, ge=0.0, le=1.0)
    sadness: float = Field(default=0.0, ge=0.0, le=1.0)
    fear: float = Field(default=0.0, ge=0.0, le=1.0)
    excitement: float = Field(default=0.0, ge=0.0, le=1.0)
    dominant: str = Field(default="neutral")


class AudioFeatures(BaseModel):
    timestamp: float
    energy: float = Field(default=0.0, description="Audio energy/loudness")
    pitch: float = Field(default=0.0, description="Pitch frequency")
    speech_rate: float = Field(default=0.0, description="Words per minute")
    intensity: float = Field(default=0.0, description="Combined intensity score")


class AttentionPoint(BaseModel):
    timestamp: float
    score: float = Field(..., ge=0.0, le=1.0, description="Attention score 0-1")
    reason: str = Field(default="", description="Why attention is high/low")


class ViralSegment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    start: float
    end: float
    duration: float
    virality_score: int = Field(..., ge=0, le=100)
    transcript: str
    emotion: EmotionData
    keywords: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list, description="Why this is viral")
    thumbnail_url: Optional[str] = None
    clip_url: Optional[str] = None


class HookRequest(BaseModel):
    segment_id: str
    job_id: str
    style: str = Field(default="curiosity", description="Hook style: curiosity, shock, challenge, story")
    count: int = Field(default=3, ge=1, le=5)


class HookResponse(BaseModel):
    hooks: List[str]
    segment_id: str
    style: str


class PersonaRequest(BaseModel):
    segment_id: str
    job_id: str
    persona: Persona
    text: str


class PersonaResponse(BaseModel):
    original_text: str
    adapted_text: str
    adapted_caption: str
    adapted_hooks: List[str]
    persona: str
    tone_description: str


class RemixRequest(BaseModel):
    segment_id: str
    job_id: str
    platform: Platform
    text: str


class RemixResponse(BaseModel):
    platform: str
    content: str
    caption: str
    hashtags: List[str]
    format_specs: Dict[str, str]
    character_count: int


class StoryRequest(BaseModel):
    job_id: str
    segment_ids: List[str]
    narrative_style: str = Field(default="problem_insight_solution")


class StoryResponse(BaseModel):
    title: str
    narrative: str
    segments_order: List[str]
    transitions: List[str]
    total_duration: float
    story_arc: str


class FaceRegion(BaseModel):
    timestamp: float
    x: float
    y: float
    width: float
    height: float
    confidence: float


class ClipExportRequest(BaseModel):
    job_id: str
    segment_id: str
    format: str = Field(default="vertical", description="vertical or horizontal")
    add_captions: bool = True
    caption_style: str = Field(default="bold_bottom")


class UploadResponse(BaseModel):
    job_id: str
    message: str
    filename: str


class StatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    current_step: str
    message: str


class AnalysisResult(BaseModel):
    job_id: str
    filename: str
    duration: float
    transcript: List[TranscriptSegment]
    segments: List[ViralSegment]
    attention_timeline: List[AttentionPoint]
    audio_features: List[AudioFeatures]
    face_regions: List[FaceRegion] = Field(default_factory=list)
    overall_stats: Dict
    processed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
