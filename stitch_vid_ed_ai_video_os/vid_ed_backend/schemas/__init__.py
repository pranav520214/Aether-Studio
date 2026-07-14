"""
VID-ED Schema Definitions
Pydantic V2 models for all JSON data contracts.
"""

from .video_cache import (
    VideoCache,
    TranscriptSegment,
    VADSegment,
    Scene,
    OCRResult,
    DetectedObject,
    DetectedFace,
    OpticalFlowData,
    AudioFeatures,
)
from .timeline import (
    Timeline,
    Track,
    Clip,
    Transform,
    Effect,
    Keyframe,
    TimelineMetadata,
)
from .creator_profile import CreatorProfile, Brand, EditingPreferences
from .hardware_profile import HardwareProfile
from .orchestrator import OrchestratorPlan, OrchestratorInput
from .validator import ValidationReport, TimelineIssue

__all__ = [
    # Video Cache
    "VideoCache",
    "TranscriptSegment",
    "VADSegment",
    "Scene",
    "OCRResult",
    "DetectedObject",
    "DetectedFace",
    "OpticalFlowData",
    "AudioFeatures",
    # Timeline
    "Timeline",
    "Track",
    "Clip",
    "Transform",
    "Effect",
    "Keyframe",
    "TimelineMetadata",
    # Creator Profile
    "CreatorProfile",
    "Brand",
    "EditingPreferences",
    # Hardware
    "HardwareProfile",
    # Orchestrator
    "OrchestratorPlan",
    "OrchestratorInput",
    # Validator
    "ValidationReport",
    "TimelineIssue",
]
