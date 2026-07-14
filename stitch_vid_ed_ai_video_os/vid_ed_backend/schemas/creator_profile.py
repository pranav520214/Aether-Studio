"""
Creator Profile Schema - Memory System data stored per creator.
Read by most agents, written only by Orchestrator or explicit user action.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal


class Brand(BaseModel):
    """Brand identity settings."""
    fonts: List[str] = Field(default_factory=list, description="Approved font family names")
    colors: List[str] = Field(default_factory=list, description="Approved color hex codes")
    logo_asset: str = Field(default="", description="Asset ID or path to logo file")

    model_config = ConfigDict(extra='forbid')


class EditingPreferences(BaseModel):
    """Creator's standing editing preferences."""
    transition_style: str = Field(default="hard_cut", description="Default transition style")
    caption_style: str = Field(default="minimal", description="Default caption style")
    music_style: str = Field(default="upbeat_electronic", description="Default music style")
    pacing: Literal["fast", "medium", "slow"] = Field(default="medium", description="Default pacing preference")

    model_config = ConfigDict(extra='forbid')


class CreatorProfile(BaseModel):
    """
    Complete creator profile stored in memory system.
    Contains brand guidelines, editing preferences, frequently used assets,
    and summaries of past projects.
    """
    creator_id: str = Field(..., description="Unique creator identifier")
    brand: Brand = Field(default_factory=Brand, description="Brand identity settings")
    editing_preferences: EditingPreferences = Field(default_factory=EditingPreferences, description="Editing preferences")
    frequently_used_assets: List[str] = Field(default_factory=list, description="List of frequently used asset IDs")
    past_projects_summary: str = Field(default="", description="Summary of past projects for context")

    model_config = ConfigDict(extra='forbid')
