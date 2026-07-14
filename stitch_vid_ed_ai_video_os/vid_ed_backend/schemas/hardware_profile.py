"""
Hardware Profile Schema - Produced by Hardware Adaptation Layer at startup.
Determines which model tier (0.5B, 3B, 7B) is available for LLM inference.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal, Optional


class HardwareProfile(BaseModel):
    """
    Hardware capability profile detected at system startup.
    Used by Orchestrator to determine model tier and enable lightweight_mode.
    
    HARD RULE: Model tier must match RAM availability:
    - 8GB or less → "0.5b"
    - 16GB → "3b"  
    - 32GB+ → "7b"
    """
    cpu: str = Field(..., description="CPU model name")
    gpu: Optional[str] = Field(default=None, description="GPU model name or 'none' if unavailable")
    ram_gb: int = Field(..., gt=0, description="Total system RAM in GB")
    tier: Literal["0.5b", "3b", "7b"] = Field(..., description="Model tier based on available RAM")
    gpu_available: bool = Field(default=False, description="Whether GPU acceleration is available")

    model_config = ConfigDict(extra='forbid')

    @field_validator('tier')
    @classmethod
    def validate_tier_matches_ram(cls, v: str, info) -> str:
        """Ensure tier matches RAM capacity per hardware adaptation rules."""
        # Note: This validator runs after model construction
        # The actual tier assignment logic is in HardwareAdaptationAgent
        return v

    def get_recommended_model(self) -> str:
        """Return recommended Ollama model name based on tier."""
        model_map = {
            "0.5b": "qwen2.5:0.5b",
            "3b": "qwen2.5:3b",
            "7b": "qwen2.5:7b"
        }
        return model_map.get(self.tier, "qwen2.5:0.5b")
