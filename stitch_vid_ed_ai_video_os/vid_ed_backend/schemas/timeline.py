"""
Timeline Schema - The ONLY file editing agents are allowed to modify.
All agents read/write to this shared timeline, never raw pixels.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal


class Keyframe(BaseModel):
    """Animation keyframe for effects or transforms."""
    time: float = Field(..., ge=0, description="Time in seconds on timeline")
    values: Dict[str, float] = Field(..., description="Key-value pairs of animated properties")
    interpolation: Literal["linear", "ease_in", "ease_out", "ease_in_out"] = Field(
        default="linear", description="Interpolation method to next keyframe"
    )

    model_config = ConfigDict(extra='forbid')


class Effect(BaseModel):
    """Effect applied to a clip."""
    type: str = Field(..., description="Effect type name, e.g., 'blur', 'glow', 'speed_ramp'")
    params: Dict[str, Any] = Field(default_factory=dict, description="Effect parameters")
    keyframes: List[Keyframe] = Field(default_factory=list, description="Animated parameter keyframes")

    model_config = ConfigDict(extra='forbid')


class Transform(BaseModel):
    """Spatial transform for a clip."""
    scale: float = Field(default=1.0, gt=0, description="Scale factor (1.0 = original size)")
    x: int = Field(default=0, description="X position offset in pixels")
    y: int = Field(default=0, description="Y position offset in pixels")
    rotation: float = Field(default=0, description="Rotation in degrees")
    crop: List[int] = Field(default=[0, 0, 0, 0], min_length=4, max_length=4, description="[left, top, right, bottom]")

    model_config = ConfigDict(extra='forbid')


class Clip(BaseModel):
    """Single clip within a track."""
    clip_id: str = Field(..., description="Unique clip ID, e.g., 'clip_001'")
    source_ref: str = Field(..., description="Reference to source video_id or asset_id")
    source_in: float = Field(..., ge=0, description="Source video in-point in seconds")
    source_out: float = Field(..., ge=0, description="Source video out-point in seconds")
    timeline_in: float = Field(..., ge=0, description="Timeline in-point in seconds")
    timeline_out: float = Field(..., ge=0, description="Timeline out-point in seconds")
    transform: Optional[Transform] = Field(default=None, description="Spatial transform")
    effects: List[Effect] = Field(default_factory=list, description="Applied effects")

    model_config = ConfigDict(extra='forbid')

    @property
    def duration(self) -> float:
        """Calculate clip duration on timeline."""
        return self.timeline_out - self.timeline_in


class Track(BaseModel):
    """A single track in the timeline (video, audio, caption, effect, overlay)."""
    track_id: str = Field(..., description="Unique track ID, e.g., 'video_01', 'audio_bgm'")
    type: Literal["video", "audio", "caption", "effect", "overlay"] = Field(..., description="Track type")
    clips: List[Clip] = Field(default_factory=list, description="Clips in this track")

    model_config = ConfigDict(extra='forbid')


class TimelineMetadata(BaseModel):
    """Timeline metadata tracking."""
    last_modified_by: str = Field(..., description="Name of agent that last modified this timeline")
    version: int = Field(default=0, ge=0, description="Version number, incremented on each edit")

    model_config = ConfigDict(extra='forbid')


class Timeline(BaseModel):
    """
    Shared Timeline Engine - the central data structure all editing agents read/write.
    Contains all tracks, clips, transforms, effects, and timing information.
    No agent ever modifies raw video/audio; they only modify this JSON.
    """
    project_id: str = Field(..., description="Unique project identifier")
    resolution: List[int] = Field(..., min_length=2, max_length=2, description="[width, height]")
    fps: float = Field(..., gt=0, description="Frames per second")
    tracks: List[Track] = Field(default_factory=list, description="All timeline tracks")
    metadata: TimelineMetadata = Field(..., description="Timeline metadata")

    model_config = ConfigDict(extra='forbid')

    def get_total_duration(self) -> float:
        """Calculate total timeline duration from all clips."""
        max_time = 0.0
        for track in self.tracks:
            for clip in track.clips:
                if clip.timeline_out > max_time:
                    max_time = clip.timeline_out
        return max_time

    def find_overlaps(self, track_id: str) -> List[tuple]:
        """Find overlapping clips within a specific track. Returns list of (clip1_id, clip2_id) tuples."""
        track = next((t for t in self.tracks if t.track_id == track_id), None)
        if not track:
            return []
        
        overlaps = []
        sorted_clips = sorted(track.clips, key=lambda c: c.timeline_in)
        for i in range(len(sorted_clips) - 1):
            if sorted_clips[i].timeline_out > sorted_clips[i + 1].timeline_in:
                overlaps.append((sorted_clips[i].clip_id, sorted_clips[i + 1].clip_id))
        return overlaps
