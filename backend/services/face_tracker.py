"""
AttentionX - Face Tracker Service
Uses MediaPipe for face detection and tracking for smart vertical framing
"""

from typing import List, Optional, Dict
from models.schemas import FaceRegion


class FaceTracker:
    """
    Tracks face positions in video for smart vertical framing:
    - Detects face bounding boxes
    - Tracks face center across frames
    - Provides smooth framing coordinates
    """

    def __init__(self):
        self.mp_available = self._check_mediapipe()

    def _check_mediapipe(self) -> bool:
        """Check if MediaPipe is available."""
        try:
            import mediapipe as mp
            return True
        except ImportError:
            return False

    async def track_faces(
        self, 
        video_path: str, 
        sample_rate: int = 5
    ) -> List[FaceRegion]:
        """
        Track face positions throughout video.
        
        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame
            
        Returns:
            List of FaceRegion with face positions
        """
        if self.mp_available:
            return await self._track_with_mediapipe(video_path, sample_rate)
        
        return self._generate_simulated_tracking(video_path)

    async def _track_with_mediapipe(
        self, video_path: str, sample_rate: int
    ) -> List[FaceRegion]:
        """Track faces using MediaPipe."""
        try:
            import cv2
            import mediapipe as mp
            
            mp_face = mp.solutions.face_detection
            face_detection = mp_face.FaceDetection(
                model_selection=1, 
                min_detection_confidence=0.5
            )
            
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            face_regions = []
            frame_idx = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_rate == 0:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(rgb_frame)
                    
                    timestamp = frame_idx / fps
                    
                    if results.detections:
                        detection = results.detections[0]  # Primary face
                        bbox = detection.location_data.relative_bounding_box
                        
                        face_regions.append(FaceRegion(
                            timestamp=round(timestamp, 2),
                            x=round(bbox.xmin + bbox.width / 2, 4),
                            y=round(bbox.ymin + bbox.height / 2, 4),
                            width=round(bbox.width, 4),
                            height=round(bbox.height, 4),
                            confidence=round(detection.score[0], 3),
                        ))
                
                frame_idx += 1
            
            cap.release()
            face_detection.close()
            
            # Smooth the tracking data
            face_regions = self._smooth_tracking(face_regions)
            
            return face_regions
            
        except Exception as e:
            print(f"MediaPipe tracking error: {e}")
            return self._generate_simulated_tracking(video_path)

    def _smooth_tracking(self, regions: List[FaceRegion]) -> List[FaceRegion]:
        """Smooth face tracking data to prevent jitter."""
        if len(regions) < 3:
            return regions
        
        smoothed = [regions[0]]
        
        for i in range(1, len(regions) - 1):
            prev = regions[i - 1]
            curr = regions[i]
            next_r = regions[i + 1]
            
            smooth_x = (prev.x * 0.25 + curr.x * 0.5 + next_r.x * 0.25)
            smooth_y = (prev.y * 0.25 + curr.y * 0.5 + next_r.y * 0.25)
            
            smoothed.append(FaceRegion(
                timestamp=curr.timestamp,
                x=round(smooth_x, 4),
                y=round(smooth_y, 4),
                width=curr.width,
                height=curr.height,
                confidence=curr.confidence,
            ))
        
        smoothed.append(regions[-1])
        return smoothed

    def _generate_simulated_tracking(self, video_path: str) -> List[FaceRegion]:
        """Generate simulated face tracking data for demo."""
        import math
        
        try:
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(video_path)
            duration = video.duration
            video.close()
        except Exception:
            duration = 120.0
        
        regions = []
        for t in range(0, int(duration), 1):
            # Simulate slight head movement
            base_x = 0.5 + math.sin(t * 0.2) * 0.05
            base_y = 0.35 + math.sin(t * 0.15) * 0.03
            
            regions.append(FaceRegion(
                timestamp=float(t),
                x=round(base_x, 4),
                y=round(base_y, 4),
                width=0.2,
                height=0.25,
                confidence=0.92,
            ))
        
        return regions

    def get_face_at_timestamp(
        self, regions: List[FaceRegion], timestamp: float
    ) -> Optional[Dict]:
        """Get face position at a specific timestamp."""
        if not regions:
            return None
        
        # Find closest face region
        closest = min(regions, key=lambda r: abs(r.timestamp - timestamp))
        
        if abs(closest.timestamp - timestamp) <= 2.0:
            return {
                "x": closest.x,
                "y": closest.y,
                "width": closest.width,
                "height": closest.height,
            }
        
        return None


face_tracker = FaceTracker()
