"""
AttentionX - Transcription Service
Uses OpenAI Whisper for high-accuracy speech-to-text with timestamps
Falls back to Gemini if Whisper is not available
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Optional
from models.schemas import TranscriptSegment


class TranscriptionService:
    """Handles speech-to-text transcription with word-level timestamps."""

    def __init__(self):
        self.whisper_available = self._check_whisper()

    def _check_whisper(self) -> bool:
        """Check if Whisper is available."""
        try:
            import whisper
            return True
        except ImportError:
            return False

    async def transcribe(self, audio_path: str, use_gemini: bool = False) -> List[TranscriptSegment]:
        """
        Transcribe audio file to text with timestamps.
        
        Args:
            audio_path: Path to the audio file
            use_gemini: Whether to use Gemini API instead of Whisper
            
        Returns:
            List of TranscriptSegment with timestamps
        """
        if use_gemini:
            return await self._transcribe_with_gemini(audio_path)
        
        if self.whisper_available:
            return await self._transcribe_with_whisper(audio_path)
        
        # Fallback to Gemini
        return await self._transcribe_with_gemini(audio_path)

    async def _transcribe_with_whisper(self, audio_path: str) -> List[TranscriptSegment]:
        """Transcribe using OpenAI Whisper locally."""
        try:
            import whisper
            
            model = whisper.load_model("base")
            result = model.transcribe(
                audio_path,
                word_timestamps=True,
                verbose=False
            )
            
            segments = []
            for seg in result.get("segments", []):
                segments.append(TranscriptSegment(
                    start=round(seg["start"], 2),
                    end=round(seg["end"], 2),
                    text=seg["text"].strip(),
                    confidence=round(seg.get("avg_logprob", -0.5) + 1, 2)
                ))
            
            return segments
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return await self._transcribe_with_gemini(audio_path)

    async def _transcribe_with_gemini(self, audio_path: str) -> List[TranscriptSegment]:
        """Transcribe using Google Gemini API."""
        try:
            import google.generativeai as genai
            from config import GEMINI_API_KEY
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            audio_file = genai.upload_file(audio_path)
            
            prompt = """Transcribe this audio with precise timestamps. 
            Return a JSON array where each element has:
            - "start": start time in seconds (float)
            - "end": end time in seconds (float)  
            - "text": the transcribed text for that segment
            
            Break into natural sentence segments of 5-15 seconds each.
            Return ONLY valid JSON, no markdown formatting."""
            
            response = model.generate_content([prompt, audio_file])
            
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            
            data = json.loads(text)
            segments = []
            for item in data:
                segments.append(TranscriptSegment(
                    start=float(item["start"]),
                    end=float(item["end"]),
                    text=item["text"].strip(),
                    confidence=0.85
                ))
            
            return segments
            
        except Exception as e:
            print(f"Gemini transcription error: {e}")
            return self._generate_fallback_segments(audio_path)

    def _generate_fallback_segments(self, audio_path: str) -> List[TranscriptSegment]:
        """Generate placeholder segments if all transcription fails."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0
        except Exception:
            duration = 120.0
        
        segments = []
        seg_duration = 10.0
        current = 0.0
        
        while current < duration:
            end = min(current + seg_duration, duration)
            segments.append(TranscriptSegment(
                start=round(current, 2),
                end=round(end, 2),
                text=f"[Segment {len(segments) + 1} - Transcription pending]",
                confidence=0.0
            ))
            current = end
        
        return segments


transcription_service = TranscriptionService()
