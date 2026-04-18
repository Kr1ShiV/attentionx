"""
AttentionX - Clip Extractor Service
Extracts video clips using MoviePy with optional face-centered framing
"""

import os
from pathlib import Path
from typing import Optional
from config import OUTPUT_DIR


class ClipExtractor:
    """Extracts and processes video clips from source video."""

    async def extract_clip(
        self,
        video_path: str,
        start: float,
        end: float,
        output_name: str,
        vertical: bool = True,
        add_captions: bool = True,
        caption_text: str = "",
        face_region: dict = None,
    ) -> Optional[str]:
        """
        Extract a clip from video with optional reframing and captions.
        
        Args:
            video_path: Path to source video
            start: Start time in seconds
            end: End time in seconds
            output_name: Name for output file
            vertical: Whether to crop to vertical (9:16)
            add_captions: Whether to add captions
            caption_text: Caption text to overlay
            face_region: Face position for centering
            
        Returns:
            Path to extracted clip or None
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            
            # Load video and extract subclip
            video = VideoFileClip(video_path)
            clip = video.subclip(start, min(end, video.duration))
            
            # Apply vertical framing if requested
            if vertical:
                clip = self._apply_vertical_framing(clip, face_region)
            
            # Add captions if requested
            if add_captions and caption_text:
                clip = self._add_captions(clip, caption_text)
            
            # Output path
            output_path = str(OUTPUT_DIR / f"{output_name}.mp4")
            
            clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=30,
                preset="ultrafast",
                verbose=False,
                logger=None,
            )
            
            clip.close()
            video.close()
            
            return output_path
            
        except ImportError:
            print("MoviePy not available for clip extraction")
            return None
        except Exception as e:
            print(f"Clip extraction error: {e}")
            return None

    def _apply_vertical_framing(self, clip, face_region: dict = None):
        """Crop clip to 9:16 vertical format, centered on face if available."""
        from moviepy.editor import VideoFileClip
        
        w, h = clip.size
        
        # Target 9:16 aspect ratio
        target_ratio = 9 / 16
        current_ratio = w / h
        
        if current_ratio > target_ratio:
            # Video is wider than target - crop width
            new_w = int(h * target_ratio)
            
            if face_region:
                # Center crop on face
                face_center_x = int(face_region.get("x", 0.5) * w)
                x1 = max(0, face_center_x - new_w // 2)
                x1 = min(x1, w - new_w)
            else:
                # Center crop
                x1 = (w - new_w) // 2
            
            clip = clip.crop(x1=x1, x2=x1 + new_w)
        
        # Resize to standard vertical resolution
        clip = clip.resize(height=1920)
        
        return clip

    def _add_captions(self, clip, caption_text: str):
        """Add styled captions to clip."""
        try:
            from moviepy.editor import TextClip, CompositeVideoClip
            
            # Split caption into chunks for readability
            words = caption_text.split()
            chunks = []
            current_chunk = []
            
            for word in words:
                current_chunk.append(word)
                if len(current_chunk) >= 5:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            if not chunks:
                return clip
            
            # Calculate duration per chunk
            duration_per_chunk = clip.duration / len(chunks)
            
            text_clips = []
            for i, chunk in enumerate(chunks):
                txt = TextClip(
                    chunk,
                    fontsize=48,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(clip.size[0] * 0.85, None),
                    align='center',
                )
                txt = txt.set_position(('center', clip.size[1] * 0.78))
                txt = txt.set_start(i * duration_per_chunk)
                txt = txt.set_duration(duration_per_chunk)
                text_clips.append(txt)
            
            return CompositeVideoClip([clip] + text_clips)
            
        except Exception as e:
            print(f"Caption overlay error: {e}")
            return clip

    async def get_clip_thumbnail(
        self, video_path: str, timestamp: float, output_name: str
    ) -> Optional[str]:
        """Extract a thumbnail frame from video at given timestamp."""
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_path)
            frame_time = min(timestamp, video.duration - 0.1)
            
            thumb_path = str(OUTPUT_DIR / f"{output_name}_thumb.jpg")
            video.save_frame(thumb_path, t=frame_time)
            video.close()
            
            return thumb_path
            
        except Exception as e:
            print(f"Thumbnail extraction error: {e}")
            return None


clip_extractor = ClipExtractor()
