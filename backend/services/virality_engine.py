"""
AttentionX - Virality Prediction Engine
Predicts which segments are likely to go viral using multi-signal analysis
"""

import json
import re
from typing import List, Dict, Tuple
from models.schemas import (
    TranscriptSegment, AudioFeatures, EmotionData, 
    ViralSegment, AttentionPoint
)
from config import VIRALITY_WEIGHTS, VIRAL_KEYWORDS, GEMINI_API_KEY


class ViralityEngine:
    """
    Predicts viral potential of video segments using:
    - Emotion detection (text sentiment + voice)
    - Speech intensity (pitch, speed, energy)
    - Keyword triggers
    - Content novelty analysis
    """

    def __init__(self):
        self.weights = VIRALITY_WEIGHTS
        self.keywords = [kw.lower() for kw in VIRAL_KEYWORDS]

    async def analyze_segments(
        self,
        transcript: List[TranscriptSegment],
        audio_features: List[AudioFeatures],
        target_duration: Tuple[int, int] = (15, 60)
    ) -> Tuple[List[ViralSegment], List[AttentionPoint]]:
        """
        Analyze transcript segments and audio features to find viral moments.
        
        Returns:
            Tuple of (viral_segments, attention_timeline)
        """
        # Step 1: Identify candidate segments (natural breakpoints)
        candidates = self._identify_candidates(transcript, target_duration)
        
        # Step 2: Score each candidate
        scored_segments = []
        for start, end, text in candidates:
            # Get audio features for this time range
            relevant_audio = [f for f in audio_features if start <= f.timestamp <= end]
            
            # Compute individual scores
            emotion_score = await self._analyze_emotion(text)
            energy_score = self._compute_energy_score(relevant_audio)
            keyword_score = self._compute_keyword_score(text)
            speech_rate_score = self._compute_speech_rate_score(relevant_audio)
            pitch_score = self._compute_pitch_score(relevant_audio)
            novelty_score = self._compute_novelty_score(text)
            
            # Weighted virality score
            virality = (
                self.weights["emotion_intensity"] * emotion_score +
                self.weights["speech_energy"] * energy_score +
                self.weights["keyword_triggers"] * keyword_score +
                self.weights["speech_rate_change"] * speech_rate_score +
                self.weights["pitch_variation"] * pitch_score +
                self.weights["content_novelty"] * novelty_score
            )
            
            virality_score = int(min(max(virality * 100, 5), 99))
            
            # Get emotion data
            emotion_data = await self._get_emotion_data(text)
            
            # Find viral keywords in text
            found_keywords = [kw for kw in self.keywords if kw in text.lower()]
            
            # Generate reasons
            reasons = self._generate_reasons(
                emotion_score, energy_score, keyword_score,
                speech_rate_score, pitch_score, found_keywords
            )
            
            segment = ViralSegment(
                start=start,
                end=end,
                duration=round(end - start, 2),
                virality_score=virality_score,
                transcript=text,
                emotion=emotion_data,
                keywords=found_keywords[:5],
                reasons=reasons,
            )
            scored_segments.append(segment)
        
        # Sort by virality score
        scored_segments.sort(key=lambda x: x.virality_score, reverse=True)
        
        # Step 3: Generate attention timeline
        attention_timeline = self._generate_attention_timeline(
            transcript, audio_features, scored_segments
        )
        
        return scored_segments, attention_timeline

    def _identify_candidates(
        self, 
        transcript: List[TranscriptSegment],
        target_duration: Tuple[int, int]
    ) -> List[Tuple[float, float, str]]:
        """Identify candidate clip segments from transcript."""
        if not transcript:
            return []
        
        candidates = []
        min_dur, max_dur = target_duration
        
        # Sliding window approach
        i = 0
        while i < len(transcript):
            # Try to build a segment of target duration
            j = i
            text_parts = []
            start = transcript[i].start
            
            while j < len(transcript):
                text_parts.append(transcript[j].text)
                end = transcript[j].end
                duration = end - start
                
                if duration >= min_dur:
                    combined_text = " ".join(text_parts)
                    candidates.append((start, end, combined_text))
                    
                    if duration >= max_dur:
                        break
                
                j += 1
            
            # Move forward by a few segments
            i += max(1, (j - i) // 2)
        
        # Deduplicate overlapping segments (keep best coverage)
        if len(candidates) > 20:
            # Sample evenly
            step = len(candidates) // 15
            candidates = candidates[::step]
        
        return candidates[:15]

    async def _analyze_emotion(self, text: str) -> float:
        """Analyze emotional intensity of text."""
        # Simple heuristic analysis
        intensity_markers = [
            "!", "?!", "...", "STOP", "NEVER", "ALWAYS",
            "amazing", "incredible", "terrible", "worst", "best",
            "love", "hate", "crucial", "critical", "urgent",
        ]
        
        text_lower = text.lower()
        score = 0.3  # Base score
        
        for marker in intensity_markers:
            if marker.lower() in text_lower:
                score += 0.08
        
        # Exclamation density
        excl_count = text.count("!")
        score += min(excl_count * 0.05, 0.2)
        
        # Question density (engagement)
        q_count = text.count("?")
        score += min(q_count * 0.04, 0.15)
        
        # Sentence length variety (more dynamic = more engaging)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) > 1:
            lengths = [len(s.split()) for s in sentences]
            if lengths:
                variety = max(lengths) - min(lengths)
                score += min(variety * 0.02, 0.1)
        
        return min(score, 1.0)

    async def _get_emotion_data(self, text: str) -> EmotionData:
        """Get detailed emotion data for text segment."""
        text_lower = text.lower()
        
        joy_words = ["happy", "great", "amazing", "wonderful", "love", "excited", "awesome"]
        surprise_words = ["wow", "incredible", "unbelievable", "shocking", "didn't expect"]
        anger_words = ["angry", "frustrated", "annoying", "terrible", "worst", "hate"]
        sadness_words = ["sad", "unfortunately", "difficult", "struggle", "pain", "lost"]
        fear_words = ["afraid", "worried", "scary", "dangerous", "risk", "threat"]
        excitement_words = ["exciting", "thrilling", "game-changer", "breakthrough", "revolutionary"]
        
        def calc_score(words):
            return min(sum(0.15 for w in words if w in text_lower) + 0.1, 1.0)
        
        scores = {
            "joy": calc_score(joy_words),
            "surprise": calc_score(surprise_words),
            "anger": calc_score(anger_words),
            "sadness": calc_score(sadness_words),
            "fear": calc_score(fear_words),
            "excitement": calc_score(excitement_words),
        }
        
        dominant = max(scores, key=scores.get)
        if max(scores.values()) < 0.2:
            dominant = "neutral"
        
        return EmotionData(
            **scores,
            dominant=dominant
        )

    def _compute_energy_score(self, audio_features: List[AudioFeatures]) -> float:
        """Compute energy score from audio features."""
        if not audio_features:
            return 0.5
        energies = [f.energy for f in audio_features]
        avg = sum(energies) / len(energies)
        peak = max(energies)
        return min((avg * 0.6 + peak * 0.4), 1.0)

    def _compute_keyword_score(self, text: str) -> float:
        """Score based on viral keyword presence."""
        text_lower = text.lower()
        found = sum(1 for kw in self.keywords if kw in text_lower)
        return min(found * 0.15, 1.0)

    def _compute_speech_rate_score(self, audio_features: List[AudioFeatures]) -> float:
        """Score based on speech rate variation (more variation = more engaging)."""
        if not audio_features:
            return 0.5
        rates = [f.speech_rate for f in audio_features if f.speech_rate > 0]
        if not rates:
            return 0.5
        
        avg_rate = sum(rates) / len(rates)
        variance = sum((r - avg_rate) ** 2 for r in rates) / len(rates)
        return min(variance * 5 + avg_rate * 0.3, 1.0)

    def _compute_pitch_score(self, audio_features: List[AudioFeatures]) -> float:
        """Score based on pitch variation."""
        if not audio_features:
            return 0.5
        pitches = [f.pitch for f in audio_features]
        if not pitches:
            return 0.5
        
        avg = sum(pitches) / len(pitches)
        variation = sum(abs(p - avg) for p in pitches) / len(pitches)
        return min(variation * 3 + 0.2, 1.0)

    def _compute_novelty_score(self, text: str) -> float:
        """Score content novelty - unique/contrarian ideas score higher."""
        novelty_patterns = [
            r"(most people|everyone) (think|believe|say)",
            r"(actually|in reality|the truth is)",
            r"(contrary to|opposite of|unlike)",
            r"(secret|hidden|unknown)",
            r"(first time|never before|breakthrough)",
            r"(misconception|myth|lie)",
        ]
        
        score = 0.3
        for pattern in novelty_patterns:
            if re.search(pattern, text.lower()):
                score += 0.12
        
        return min(score, 1.0)

    def _generate_reasons(
        self, emotion, energy, keyword, speech_rate, pitch, keywords
    ) -> List[str]:
        """Generate human-readable reasons for virality score."""
        reasons = []
        
        if emotion > 0.6:
            reasons.append("🔥 High emotional intensity detected")
        if energy > 0.7:
            reasons.append("⚡ Peak audio energy in this segment")
        if keyword > 0.3:
            reasons.append(f"🎯 Contains viral triggers: {', '.join(keywords[:3])}")
        if speech_rate > 0.6:
            reasons.append("🗣️ Dynamic speech pacing creates engagement")
        if pitch > 0.6:
            reasons.append("📈 Significant pitch variation signals passion")
        if emotion > 0.4 and energy > 0.5:
            reasons.append("💎 Strong emotional + energy combination")
        
        if not reasons:
            reasons.append("📊 Moderate viral potential based on content analysis")
        
        return reasons

    def _generate_attention_timeline(
        self,
        transcript: List[TranscriptSegment],
        audio_features: List[AudioFeatures],
        segments: List[ViralSegment]
    ) -> List[AttentionPoint]:
        """Generate attention heatmap timeline."""
        if not audio_features:
            return []
        
        timeline = []
        
        for feature in audio_features:
            t = feature.timestamp
            
            # Base score from audio intensity
            base_score = (feature.energy * 0.4 + feature.intensity * 0.4 + feature.pitch * 0.2)
            
            # Boost if this timestamp is within a high-virality segment
            boost = 0.0
            reason = "Baseline engagement"
            for seg in segments:
                if seg.start <= t <= seg.end:
                    boost = seg.virality_score / 200.0  # 0-0.5 boost
                    if seg.virality_score > 70:
                        reason = "🔥 High virality zone"
                    elif seg.virality_score > 50:
                        reason = "📈 Rising engagement"
                    break
            
            score = min(base_score + boost, 1.0)
            
            timeline.append(AttentionPoint(
                timestamp=t,
                score=round(score, 3),
                reason=reason
            ))
        
        return timeline


virality_engine = ViralityEngine()
