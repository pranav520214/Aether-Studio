"""
Validator Schema - Output from TimelineValidator Agent (Agent 15).
Validates timeline.json for overlaps, gaps, and dangling references before rendering.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal


class TimelineIssue(BaseModel):
    """A single validation issue found in the timeline."""
    issue_id: str = Field(..., description="Unique issue ID, e.g., 'issue_001'")
    severity: Literal["error", "warning", "info"] = Field(..., description="Issue severity level")
    category: Literal["overlap", "gap", "dangling_ref", "timing", "transform", "effect", "audio"] = Field(
        ..., description="Category of the issue"
    )
    track_id: Optional[str] = Field(default=None, description="Affected track ID if applicable")
    clip_id: Optional[str] = Field(default=None, description="Affected clip ID if applicable")
    description: str = Field(..., description="Human-readable description of the issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix for the issue")

    model_config = ConfigDict(extra='forbid')


class ValidationReport(BaseModel):
    """
    Complete validation report from TimelineValidator Agent.
    Rendering must NOT proceed if any 'error' severity issues exist.
    
    HARD RULE: The render engine must check is_valid() before proceeding.
    """
    project_id: str = Field(..., description="Project ID being validated")
    timeline_version: int = Field(..., ge=0, description="Version of timeline that was validated")
    is_valid: bool = Field(..., description="True if no 'error' severity issues exist")
    issues: List[TimelineIssue] = Field(default_factory=list, description="List of all validation issues")
    error_count: int = Field(default=0, ge=0, description="Count of error-level issues")
    warning_count: int = Field(default=0, ge=0, description="Count of warning-level issues")
    info_count: int = Field(default=0, ge=0, description="Count of info-level issues")

    model_config = ConfigDict(extra='forbid')

    def model_post_init(self, __context) -> None:
        """Auto-calculate counts after initialization."""
        self.error_count = sum(1 for i in self.issues if i.severity == "error")
        self.warning_count = sum(1 for i in self.issues if i.severity == "warning")
        self.info_count = sum(1 for i in self.issues if i.severity == "info")
        self.is_valid = self.error_count == 0

    def get_errors(self) -> List[TimelineIssue]:
        """Return only error-level issues."""
        return [i for i in self.issues if i.severity == "error"]

    def get_warnings(self) -> List[TimelineIssue]:
        """Return only warning-level issues."""
        return [i for i in self.issues if i.severity == "warning"]
