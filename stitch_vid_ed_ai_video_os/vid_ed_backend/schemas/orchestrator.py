"""
Orchestrator Schema - Input/Output for the Orchestrator/Director Agent.
This is the ONLY agent that reads free-text user instructions.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Literal


class OrchestratorInput(BaseModel):
    """
    Input to the Orchestrator Agent.
    Contains user request, creator profile, hardware profile, and project state.
    """
    user_request: str = Field(..., description="Free text instruction from the user")
    creator_profile: Dict = Field(default_factory=dict, description="Creator profile data")
    hardware_profile: Dict = Field(default_factory=dict, description="Hardware profile data")
    project_state: Dict = Field(
        default_factory=lambda: {"has_existing_timeline": False, "video_ids": []},
        description="Current project state"
    )

    model_config = ConfigDict(extra='forbid')


class OrchestratorPlan(BaseModel):
    """
    Editing Plan produced by the Orchestrator Agent.
    This plan determines which agents run and in what order.
    
    HARD RULES enforced by this schema:
    1. dispatch_order must only contain agents from the fixed list
    2. Every dispatched agent must have a matching instruction in agent_instructions
    3. If clarification_needed is set, dispatch_order must be empty
    4. lightweight_mode must match hardware_profile.tier ("0.5b" → True)
    """
    plan_id: str = Field(..., description="Unique plan ID, format: 'plan_' + 6 alphanumeric chars")
    interpreted_goal: str = Field(..., description="One-sentence restatement of user's goal")
    target_platform: Literal[
        "instagram_reels", "tiktok", "youtube_shorts", 
        "youtube_long", "generic", "unspecified"
    ] = Field(..., description="Target platform for the video")
    style_reference: Optional[str] = Field(default=None, description="Style reference description")
    lightweight_mode: bool = Field(default=False, description="Enable lightweight mode for 0.5B tier")
    dispatch_order: List[str] = Field(
        default_factory=list, 
        description="Ordered list of agents to dispatch"
    )
    agent_instructions: Dict[str, str] = Field(
        default_factory=dict, 
        description="One imperative instruction per dispatched agent"
    )
    assumptions: List[str] = Field(default_factory=list, description="List of assumptions made")
    clarification_needed: Optional[str] = Field(default=None, description="Clarification question if needed")
    needs_analysis: bool = Field(default=False, description="Whether video analysis is needed first")

    model_config = ConfigDict(extra='forbid')

    # Fixed list of valid agent names per system prompt
    VALID_AGENTS = frozenset({
        "research_agent", "story_agent", "brand_agent", "caption_agent", 
        "motion_agent", "audio_agent", "voice_agent", "color_agent", 
        "vfx_agent", "thumbnail_agent", "music_agent", "broll_agent", 
        "shorts_agent"
    })

    # Fixed dispatch order (relative ordering must be preserved)
    FIXED_ORDER = [
        "research_agent", "story_agent", "brand_agent", "broll_agent",
        "motion_agent", "color_agent", "audio_agent", "voice_agent",
        "music_agent", "caption_agent", "vfx_agent", "thumbnail_agent",
        "shorts_agent"
    ]

    def validate_dispatch_order(self) -> bool:
        """Validate dispatch_order contains only valid agents in correct relative order."""
        if not self.dispatch_order:
            return True
        
        # Check all agents are valid
        for agent in self.dispatch_order:
            if agent not in self.VALID_AGENTS:
                return False
        
        # Check relative order matches fixed order
        positions = {agent: i for i, agent in enumerate(self.FIXED_ORDER)}
        last_position = -1
        for agent in self.dispatch_order:
            current_position = positions.get(agent, -1)
            if current_position < last_position:
                return False
            last_position = current_position
        
        return True

    def validate_instructions_match(self) -> bool:
        """Validate every dispatched agent has a corresponding instruction."""
        for agent in self.dispatch_order:
            if agent not in self.agent_instructions:
                return False
            if not self.agent_instructions[agent].strip():
                return False
        return True

    def validate_clarification_rule(self) -> bool:
        """If clarification_needed is set, dispatch_order must be empty."""
        if self.clarification_needed is not None:
            return len(self.dispatch_order) == 0
        return True
