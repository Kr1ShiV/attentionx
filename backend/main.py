"""
AttentionX - AI Content Intelligence Engine
FastAPI Backend - Main Application

Transforms long-form videos into viral-ready short-form content
with AI-powered analysis, virality prediction, and multi-platform optimization.
"""

import os
import sys
import uuid
import json
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import UPLOAD_DIR, OUTPUT_DIR, MAX_VIDEO_SIZE_MB
from models.schemas import (
    JobStatus, UploadResponse, StatusResponse, AnalysisResult,
    HookRequest, HookResponse, PersonaRequest, PersonaResponse,
    RemixRequest, RemixResponse, StoryRequest, StoryResponse,
    ClipExportRequest, ViralSegment,
)
from services.transcription import transcription_service
from services.audio_analyzer import audio_analyzer
from services.virality_engine import virality_engine
from services.hook_generator import hook_generator
from services.persona_adapter import persona_adapter
from services.clip_extractor import clip_extractor
from services.story_builder import story_builder
from services.remix_engine import remix_engine
from services.face_tracker import face_tracker

# ─── App Setup ────────────────────────────────────────────────

app = FastAPI(
    title="AttentionX",
    description="AI-Powered Content Intelligence Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Serve outputs
if OUTPUT_DIR.exists():
    app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

# ─── In-Memory Job Store ──────────────────────────────────────

jobs: Dict[str, dict] = {}


def get_job(job_id: str) -> dict:
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return jobs[job_id]


# ─── Routes ───────────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the frontend."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "AttentionX API is running", "docs": "/docs"}


@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.now().isoformat()}


# ─── Upload & Processing ─────────────────────────────────────

@app.post("/api/upload", response_model=UploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a video file and start processing."""
    # Validate file type
    allowed_types = {
        "video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo",
        "video/webm", "video/x-matroska",
    }
    
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")
    
    # Generate job ID
    job_id = str(uuid.uuid4())[:12]
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        if len(content) > MAX_VIDEO_SIZE_MB * 1024 * 1024:
            raise HTTPException(400, f"File too large. Max size: {MAX_VIDEO_SIZE_MB}MB")
        f.write(content)
    
    # Initialize job
    jobs[job_id] = {
        "id": job_id,
        "filename": file.filename,
        "file_path": str(file_path),
        "status": JobStatus.PENDING,
        "progress": 0,
        "current_step": "Queued for processing",
        "message": "Video uploaded successfully",
        "result": None,
        "created_at": datetime.now().isoformat(),
    }
    
    # Start background processing
    background_tasks.add_task(process_video, job_id)
    
    return UploadResponse(
        job_id=job_id,
        message="Video uploaded. Processing started.",
        filename=file.filename,
    )


async def process_video(job_id: str):
    """Background task to process uploaded video."""
    job = jobs[job_id]
    video_path = job["file_path"]
    
    try:
        # ── Step 1: Extract Audio ──
        job["status"] = JobStatus.EXTRACTING_AUDIO
        job["progress"] = 10
        job["current_step"] = "Extracting audio from video"
        
        audio_path = await extract_audio(video_path, job_id)
        
        # ── Step 2: Transcribe ──
        job["status"] = JobStatus.TRANSCRIBING
        job["progress"] = 25
        job["current_step"] = "Transcribing speech to text"
        
        transcript = await transcription_service.transcribe(audio_path)
        
        # ── Step 3: Analyze Audio ──
        job["status"] = JobStatus.ANALYZING_AUDIO
        job["progress"] = 40
        job["current_step"] = "Analyzing audio patterns"
        
        audio_features = await audio_analyzer.analyze(audio_path)
        
        # Update speech rate with transcript data
        audio_features = audio_analyzer.compute_speech_rate(audio_features, transcript)
        
        # ── Step 4: Track Faces ──
        job["status"] = JobStatus.DETECTING_FACES
        job["progress"] = 55
        job["current_step"] = "Detecting and tracking faces"
        
        face_regions = await face_tracker.track_faces(video_path)
        
        # ── Step 5: Score Virality ──
        job["status"] = JobStatus.SCORING_VIRALITY
        job["progress"] = 70
        job["current_step"] = "Predicting viral moments"
        
        segments, attention_timeline = await virality_engine.analyze_segments(
            transcript, audio_features
        )
        
        # Generate hooks for top segments
        for seg in segments[:5]:
            seg.hooks = await hook_generator.generate_hooks(seg.transcript, "curiosity", 3)
        
        # ── Step 6: Generate Clips ──
        job["status"] = JobStatus.GENERATING_CLIPS
        job["progress"] = 85
        job["current_step"] = "Preparing clip previews"
        
        # Get video duration
        duration = await get_video_duration(video_path)
        
        # Build result
        overall_stats = {
            "total_duration": round(duration, 2),
            "segments_found": len(segments),
            "avg_virality_score": round(
                sum(s.virality_score for s in segments) / max(len(segments), 1), 1
            ),
            "top_score": max((s.virality_score for s in segments), default=0),
            "high_virality_count": sum(1 for s in segments if s.virality_score >= 70),
            "transcript_word_count": sum(len(s.text.split()) for s in transcript),
        }
        
        result = AnalysisResult(
            job_id=job_id,
            filename=job["filename"],
            duration=duration,
            transcript=transcript,
            segments=segments,
            attention_timeline=attention_timeline,
            audio_features=audio_features,
            face_regions=face_regions,
            overall_stats=overall_stats,
        )
        
        job["result"] = result.model_dump()
        job["status"] = JobStatus.COMPLETED
        job["progress"] = 100
        job["current_step"] = "Analysis complete"
        job["message"] = f"Found {len(segments)} viral segments with avg score {overall_stats['avg_virality_score']}"
        
    except Exception as e:
        job["status"] = JobStatus.FAILED
        job["progress"] = 0
        job["current_step"] = "Processing failed"
        job["message"] = str(e)
        print(f"Processing error for job {job_id}: {e}")
        import traceback
        traceback.print_exc()


async def extract_audio(video_path: str, job_id: str) -> str:
    """Extract audio from video file."""
    audio_path = str(UPLOAD_DIR / f"{job_id}_audio.wav")
    
    try:
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        video.close()
    except ImportError:
        # Try ffmpeg directly
        import subprocess
        try:
            subprocess.run(
                ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
                 "-ar", "22050", "-ac", "1", audio_path, "-y"],
                capture_output=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Create empty audio file as last resort
            Path(audio_path).touch()
    
    return audio_path


async def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds."""
    try:
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(video_path)
        duration = video.duration
        video.close()
        return duration
    except Exception:
        return 120.0  # Default


# ─── Status & Results ─────────────────────────────────────────

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Get processing status for a job."""
    job = get_job(job_id)
    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        message=job["message"],
    )


@app.get("/api/analysis/{job_id}")
async def get_analysis(job_id: str):
    """Get full analysis results."""
    job = get_job(job_id)
    
    if job["status"] != JobStatus.COMPLETED:
        return JSONResponse(
            status_code=202,
            content={
                "status": job["status"],
                "progress": job["progress"],
                "message": "Processing not yet complete",
            }
        )
    
    return job["result"]


# ─── Hook Generation ──────────────────────────────────────────

@app.post("/api/generate-hooks", response_model=HookResponse)
async def generate_hooks(request: HookRequest):
    """Generate viral hooks for a segment."""
    job = get_job(request.job_id)
    
    if not job.get("result"):
        raise HTTPException(400, "Analysis not complete")
    
    # Find segment
    segment = None
    for seg in job["result"]["segments"]:
        if seg["id"] == request.segment_id:
            segment = seg
            break
    
    if not segment:
        raise HTTPException(404, f"Segment {request.segment_id} not found")
    
    hooks = await hook_generator.generate_hooks(
        segment["transcript"], request.style, request.count
    )
    
    return HookResponse(
        hooks=hooks,
        segment_id=request.segment_id,
        style=request.style,
    )


# ─── Persona Adaptation ──────────────────────────────────────

@app.post("/api/adapt-persona", response_model=PersonaResponse)
async def adapt_persona(request: PersonaRequest):
    """Adapt content for a target audience persona."""
    result = await persona_adapter.adapt(request.text, request.persona.value)
    
    return PersonaResponse(
        original_text=result["original_text"],
        adapted_text=result["adapted_text"],
        adapted_caption=result["adapted_caption"],
        adapted_hooks=result["adapted_hooks"],
        persona=result["persona"],
        tone_description=result["tone_description"],
    )


# ─── Content Remix ────────────────────────────────────────────

@app.post("/api/remix", response_model=RemixResponse)
async def remix_content(request: RemixRequest):
    """Remix content for a specific platform."""
    result = await remix_engine.remix(request.text, request.platform.value)
    
    return RemixResponse(
        platform=result["platform"],
        content=result["content"],
        caption=result["caption"],
        hashtags=result["hashtags"],
        format_specs=result["format_specs"],
        character_count=result["character_count"],
    )


# ─── Story Builder ────────────────────────────────────────────

@app.post("/api/story-builder", response_model=StoryResponse)
async def build_story(request: StoryRequest):
    """Build a narrative story from selected segments."""
    job = get_job(request.job_id)
    
    if not job.get("result"):
        raise HTTPException(400, "Analysis not complete")
    
    # Get selected segments
    all_segments = job["result"]["segments"]
    selected = []
    
    for seg_data in all_segments:
        if seg_data["id"] in request.segment_ids:
            selected.append(ViralSegment(**seg_data))
    
    if not selected:
        # Use top 3 segments
        sorted_segs = sorted(all_segments, key=lambda x: x["virality_score"], reverse=True)
        selected = [ViralSegment(**s) for s in sorted_segs[:3]]
    
    result = await story_builder.build_story(selected, request.narrative_style)
    
    return StoryResponse(
        title=result["title"],
        narrative=result["narrative"],
        segments_order=result["segments_order"],
        transitions=result["transitions"],
        total_duration=result["total_duration"],
        story_arc=result["story_arc"],
    )


# ─── Clip Export ──────────────────────────────────────────────

@app.post("/api/export-clip")
async def export_clip(request: ClipExportRequest):
    """Export a processed clip."""
    job = get_job(request.job_id)
    
    if not job.get("result"):
        raise HTTPException(400, "Analysis not complete")
    
    # Find segment
    segment = None
    for seg in job["result"]["segments"]:
        if seg["id"] == request.segment_id:
            segment = seg
            break
    
    if not segment:
        raise HTTPException(404, f"Segment {request.segment_id} not found")
    
    # Extract clip
    clip_path = await clip_extractor.extract_clip(
        video_path=job["file_path"],
        start=segment["start"],
        end=segment["end"],
        output_name=f"{request.job_id}_{request.segment_id}",
        vertical=(request.format == "vertical"),
        add_captions=request.add_captions,
        caption_text=segment["transcript"],
    )
    
    if clip_path and Path(clip_path).exists():
        return FileResponse(
            clip_path,
            media_type="video/mp4",
            filename=f"attentionx_clip_{request.segment_id}.mp4",
        )
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "Clip export initiated",
            "segment_id": request.segment_id,
            "download_url": f"/outputs/{request.job_id}_{request.segment_id}.mp4",
        }
    )


# ─── Demo Data Endpoint ──────────────────────────────────────

@app.get("/api/demo")
async def get_demo_data():
    """Get demo data for frontend testing without video upload."""
    import random
    import math
    
    duration = 180.0  # 3-minute demo video
    
    # Generate transcript
    demo_sentences = [
        "Welcome to this masterclass on building products that people actually want.",
        "The biggest mistake I see founders make is building something nobody asked for.",
        "Let me tell you a secret that changed how I think about product development.",
        "Most people think you need a perfect product to launch. That's completely wrong.",
        "The truth is, your first version should be embarrassingly simple.",
        "I spent three years building the wrong thing. Here's what I learned.",
        "Stop focusing on features. Start focusing on the one problem you solve.",
        "The game-changer was when I realized users don't care about your technology.",
        "They care about whether you solve their problem faster than the alternative.",
        "If you're building a startup right now, stop and listen to this carefully.",
        "The number one reason startups fail isn't money. It's building the wrong thing.",
        "Here's the framework I use: Problem, Solution, Validation. In that order.",
        "Never skip validation. I made this mistake and it cost me everything.",
        "The best products I've built started with a conversation, not a codebase.",
        "Talk to 50 users before writing a single line of code. This is non-negotiable.",
        "Here's the shocking truth: your idea doesn't matter. Execution is everything.",
        "The difference between a successful startup and a failed one is speed.",
        "Move fast, break things, but always listen to your users.",
    ]
    
    transcript = []
    current_time = 0.0
    for i, sentence in enumerate(demo_sentences):
        seg_duration = random.uniform(7.0, 12.0)
        transcript.append({
            "start": round(current_time, 2),
            "end": round(current_time + seg_duration, 2),
            "text": sentence,
            "confidence": round(random.uniform(0.85, 0.98), 2),
        })
        current_time += seg_duration
    
    duration = current_time
    
    # Generate segments with virality scores
    segments = []
    viral_indices = [2, 3, 5, 7, 10, 12, 15]  # High-virality sentences
    
    for idx in range(0, len(demo_sentences) - 1, 2):
        start = transcript[idx]["start"]
        end = transcript[min(idx + 1, len(transcript) - 1)]["end"]
        text = " ".join([transcript[i]["text"] for i in range(idx, min(idx + 2, len(transcript)))])
        
        is_viral = idx in viral_indices
        base_score = random.randint(65, 95) if is_viral else random.randint(25, 60)
        
        emotions = ["excitement", "surprise", "joy", "neutral"]
        dominant = random.choice(emotions[:2]) if is_viral else random.choice(emotions[2:])
        
        keywords = []
        for kw in ["secret", "mistake", "truth", "game-changer", "shocking", "never", "stop"]:
            if kw in text.lower():
                keywords.append(kw)
        
        reasons = []
        if base_score > 70:
            reasons.append("🔥 High emotional intensity detected")
            reasons.append("⚡ Peak audio energy in this segment")
        if keywords:
            reasons.append(f"🎯 Contains viral triggers: {', '.join(keywords)}")
        if base_score > 60:
            reasons.append("🗣️ Dynamic speech pacing creates engagement")
        if not reasons:
            reasons.append("📊 Moderate viral potential")
        
        segments.append({
            "id": str(uuid.uuid4())[:8],
            "start": start,
            "end": end,
            "duration": round(end - start, 2),
            "virality_score": base_score,
            "transcript": text,
            "emotion": {
                "joy": round(random.uniform(0.1, 0.8), 2),
                "surprise": round(random.uniform(0.1, 0.9), 2) if is_viral else round(random.uniform(0.1, 0.3), 2),
                "anger": round(random.uniform(0.0, 0.2), 2),
                "sadness": round(random.uniform(0.0, 0.15), 2),
                "fear": round(random.uniform(0.0, 0.1), 2),
                "excitement": round(random.uniform(0.4, 0.95), 2) if is_viral else round(random.uniform(0.1, 0.4), 2),
                "dominant": dominant,
            },
            "keywords": keywords,
            "hooks": [
                f"Nobody tells you this about {text.split()[3:6] and ' '.join(text.split()[3:6]) or 'success'}…",
                f"This mistake cost me 3 years of wasted effort",
                f"If you're building a startup, STOP and watch this",
            ],
            "reasons": reasons,
            "thumbnail_url": None,
            "clip_url": None,
        })
    
    segments.sort(key=lambda x: x["virality_score"], reverse=True)
    
    # Generate attention timeline
    attention_timeline = []
    for t in range(int(duration)):
        base = 0.3
        for seg in segments:
            if seg["start"] <= t <= seg["end"]:
                base = seg["virality_score"] / 120.0 + 0.2
                break
        
        noise = random.uniform(-0.08, 0.08)
        wave = math.sin(t * 0.15) * 0.1
        score = max(0.05, min(0.98, base + noise + wave))
        
        reason = "Baseline"
        if score > 0.7:
            reason = "🔥 High virality zone"
        elif score > 0.5:
            reason = "📈 Rising engagement"
        elif score < 0.25:
            reason = "📉 Drop-off zone"
        
        attention_timeline.append({
            "timestamp": float(t),
            "score": round(score, 3),
            "reason": reason,
        })
    
    # Audio features
    audio_features = []
    for t in range(int(duration)):
        phase1 = math.sin(t * 0.12) * 0.3 + 0.45
        phase2 = math.sin(t * 0.08 + 1.5) * 0.25 + 0.5
        phase3 = math.sin(t * 0.1 + 0.7) * 0.2 + 0.5
        noise = random.uniform(0, 0.12)
        
        # Boost during viral segments
        boost = 0
        for seg in segments:
            if seg["start"] <= t <= seg["end"] and seg["virality_score"] > 65:
                boost = 0.2
                break
        
        audio_features.append({
            "timestamp": float(t),
            "energy": round(max(0, min(1, phase1 + noise + boost)), 4),
            "pitch": round(max(0, min(1, phase2 + noise * 0.5 + boost * 0.5)), 4),
            "speech_rate": round(max(0, min(1, phase3 + noise * 0.3)), 4),
            "intensity": round(max(0, min(1, (phase1 + phase2) / 2 + noise + boost)), 4),
        })
    
    overall_stats = {
        "total_duration": round(duration, 2),
        "segments_found": len(segments),
        "avg_virality_score": round(sum(s["virality_score"] for s in segments) / len(segments), 1),
        "top_score": max(s["virality_score"] for s in segments),
        "high_virality_count": sum(1 for s in segments if s["virality_score"] >= 70),
        "transcript_word_count": sum(len(s["text"].split()) for s in transcript),
    }
    
    return {
        "job_id": "demo-001",
        "filename": "startup_masterclass.mp4",
        "duration": duration,
        "transcript": transcript,
        "segments": segments,
        "attention_timeline": attention_timeline,
        "audio_features": audio_features,
        "face_regions": [],
        "overall_stats": overall_stats,
        "processed_at": datetime.now().isoformat(),
    }


# ─── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
