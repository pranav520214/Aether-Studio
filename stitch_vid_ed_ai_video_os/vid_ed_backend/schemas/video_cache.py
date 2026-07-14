"""
Video Cache Schema - Read-only metadata produced by Video Understanding Layer.
Every field is strictly typed. No agent may modify this file after initial creation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal


class TranscriptSegment(BaseModel):
    """Single transcript segment from Whisper."""
    id: str = Field(..., description="Unique segment ID, e.g., 't001'")
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    speaker: str = Field(..., description="Speaker ID, e.g., 'spk_1'")
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")

    model_config = ConfigDict(extra='forbid')


class VADSegment(BaseModel):
    """Voice Activity Detection segment."""
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    type: Literal["speech", "silence", "noise"] = Field(..., description="Segment type")

    model_config = ConfigDict(extra='forbid')


class Scene(BaseModel):
    """Detected scene/cut in the video."""
    id: str = Field(..., description="Unique scene ID, e.g., 'sc001'")
    start: float = Field(..., ge=0, description="Scene start time in seconds")
    end: float = Field(..., ge=0, description="Scene end time in seconds")
    cut_type: Literal["hard", "soft", "match"] = Field(..., description="Type of cut")

    model_config = ConfigDict(extra='forbid')


class OCRResult(BaseModel):
    """OCR-detected text in video frames."""
    id: str = Field(..., description="Unique OCR result ID, e.g., 'ocr001'")
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    text: str = Field(..., description="Detected text")
    bbox: List[int] = Field(..., min_length=4, max_length=4, description="[x, y, w, h]")

    model_config = ConfigDict(extra='forbid')


class DetectedObject(BaseModel):
    """YOLO11-detected object."""
    id: str = Field(..., description="Unique object ID, e.g., 'obj001'")
    frame_range: List[int] = Field(..., min_length=2, max_length=2, description="[start_frame, end_frame]")
    class_name: str = Field(..., alias="class", description="Object class name")
    bbox: List[int] = Field(..., min_length=4, max_length=4, description="[x, y, w, h]")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence 0-1")

    model_config = ConfigDict(extra='forbid', populate_by_name=True)


class DetectedFace(BaseModel):
    """MediaPipe-detected face."""
    id: str = Field(..., description="Unique face ID, e.g., 'face001'")
    track_range: List[int] = Field(..., min_length=2, max_length=2, description="[start_frame, end_frame]")
    bbox: List[int] = Field(..., min_length=4, max_length=4, description="[x, y, w, h]")
    emotion: str = Field(..., description="Detected emotion label")
    emotion_confidence: float = Field(..., ge=0, le=1, description="Emotion confidence 0-1")

    model_config = ConfigDict(extra='forbid')


class OpticalFlowData(BaseModel):
    """Optical flow motion data."""
    frame_range: List[int] = Field(..., min_length=2, max_length=2, description="[start_frame, end_frame]")
    avg_motion_magnitude: float = Field(..., ge=0, description="Average motion magnitude")
    direction: str = Field(..., description="Dominant motion direction, e.g., 'left', 'right', 'up', 'down'")

    model_config = ConfigDict(extra='forbid')


class AudioFeatures(BaseModel):
    """Audio analysis features."""
    loudness_lufs: float = Field(..., description="Integrated loudness in LUFS")
    peak_db: float = Field(..., description="Peak level in dB")
    noise_floor_db: float = Field(..., description="Noise floor level in dB")
    silence_ranges: List[List[float]] = Field(..., description="List of [start, end] silence ranges in seconds")

    model_config = ConfigDict(extra='forbid')


class VideoCache(BaseModel):
    """
    Complete video metadata cache. Produced once by Video Understanding Layer.
    Read-only to all downstream agents. If a fact is missing, agents must flag it,
    never guess.
    """
    video_id: str = Field(..., description="Unique video identifier")
    duration_sec: float = Field(..., gt=0, description="Total video duration in seconds")
    fps: float = Field(..., gt=0, description="Frames per second")
    resolution: List[int] = Field(..., min_length=2, max_length=2, description="[width, height]")
    transcript: List[TranscriptSegment] = Field(default_factory=list, description="Speech transcript segments")
    vad_segments: List[VADSegment] = Field(default_factory=list, description="Voice activity detection segments")
    scenes: List[Scene] = Field(default_factory=list, description="Detected scenes/cuts")
    ocr: List[OCRResult] = Field(default_factory=list, description="OCR-detected text")
    objects: List[DetectedObject] = Field(default_factory=list, description="Detected objects")
    faces: List[DetectedFace] = Field(default_factory=list, description="Detected faces")
    optical_flow: List[OpticalFlowData] = Field(default_factory=list, description="Optical flow data")
    audio_features: Optional[AudioFeatures] = Field(default=None, description="Audio analysis features")

    model_config = ConfigDict(extra='forbid')
