"""
Privantrix AI OS - Model Router
Intelligent model selection based on capabilities, latency, and quality
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ModelCapability:
    """Model capability definition"""
    name: str
    min_score: float = 0.0
    is_required: bool = False


@dataclass
class RegisteredModel:
    """Registered model with metadata"""
    id: str
    name: str
    endpoint: str
    capabilities: List[str] = field(default_factory=list)
    priority: int = 0
    context_length: int = 4096
    max_tokens: int = 2048
    latency_ms: float = 0.0
    quality_score: float = 0.5
    memory_usage_mb: float = 0.0
    specialization: Optional[str] = None
    is_active: bool = True
    last_used: Optional[str] = None
    total_requests: int = 0
    successful_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "priority": self.priority,
            "context_length": self.context_length,
            "max_tokens": self.max_tokens,
            "latency_ms": self.latency_ms,
            "quality_score": self.quality_score,
            "memory_usage_mb": self.memory_usage_mb,
            "specialization": self.specialization,
            "is_active": self.is_active,
            "last_used": self.last_used,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests
        }


class ModelRouter:
    """Routes requests to optimal models based on requirements"""
    
    def __init__(self, config_path: str = "configs/models.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._models: Dict[str, RegisteredModel] = {}
        self._request_history: List[Dict[str, Any]] = []
        self._load_models()
    
    def _load_models(self) -> None:
        """Load registered models from config"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                for model_data in data.get("models", []):
                    model = RegisteredModel(**model_data)
                    self._models[model.id] = model
    
    def _save_models(self) -> None:
        """Save models to config"""
        data = {"models": [m.to_dict() for m in self._models.values()]}
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_model(
        self,
        model_id: str,
        name: str,
        endpoint: str,
        capabilities: Optional[List[str]] = None,
        priority: int = 0,
        context_length: int = 4096,
        specialization: Optional[str] = None
    ) -> RegisteredModel:
        """Register a new model"""
        model = RegisteredModel(
            id=model_id,
            name=name,
            endpoint=endpoint,
            capabilities=capabilities or [],
            priority=priority,
            context_length=context_length,
            specialization=specialization
        )
        self._models[model_id] = model
        self._save_models()
        return model
    
    def unregister_model(self, model_id: str) -> bool:
        """Unregister a model"""
        if model_id in self._models:
            del self._models[model_id]
            self._save_models()
            return True
        return False
    
    def get_model(self, model_id: str) -> Optional[RegisteredModel]:
        """Get a model by ID"""
        return self._models.get(model_id)
    
    def list_models(self, active_only: bool = False) -> List[RegisteredModel]:
        """List all registered models"""
        models = list(self._models.values())
        if active_only:
            models = [m for m in models if m.is_active]
        return sorted(models, key=lambda m: (-m.priority, m.name))
    
    def select_model(
        self,
        required_capabilities: Optional[List[str]] = None,
        min_context_length: int = 0,
        max_latency_ms: Optional[float] = None,
        min_quality_score: float = 0.0,
        specialization: Optional[str] = None,
        prefer_low_memory: bool = False
    ) -> Optional[RegisteredModel]:
        """Select the best model for given requirements"""
        candidates = [m for m in self._models.values() if m.is_active]
        
        # Filter by required capabilities
        if required_capabilities:
            candidates = [
                m for m in candidates
                if all(cap in m.capabilities for cap in required_capabilities)
            ]
        
        # Filter by context length
        if min_context_length > 0:
            candidates = [m for m in candidates if m.context_length >= min_context_length]
        
        # Filter by latency
        if max_latency_ms is not None:
            candidates = [m for m in candidates if m.latency_ms <= max_latency_ms]
        
        # Filter by quality score
        candidates = [m for m in candidates if m.quality_score >= min_quality_score]
        
        # Filter by specialization
        if specialization:
            specialized = [m for m in candidates if m.specialization == specialization]
            if specialized:
                candidates = specialized
        
        if not candidates:
            return None
        
        # Score candidates
        def score_model(model: RegisteredModel) -> float:
            score = 0.0
            
            # Priority weight
            score += model.priority * 10
            
            # Quality score weight
            score += model.quality_score * 20
            
            # Latency penalty (lower is better)
            score -= model.latency_ms * 0.1
            
            # Memory penalty if preferred
            if prefer_low_memory:
                score -= model.memory_usage_mb * 0.05
            
            # Usage history bonus
            if model.total_requests > 0:
                success_rate = model.successful_requests / model.total_requests
                score += success_rate * 15
            
            return score
        
        candidates.sort(key=score_model, reverse=True)
        return candidates[0]
    
    def record_request(self, model_id: str, success: bool, latency_ms: float) -> None:
        """Record a request for model statistics"""
        if model_id in self._models:
            model = self._models[model_id]
            model.total_requests += 1
            if success:
                model.successful_requests += 1
            model.latency_ms = (model.latency_ms * 0.9) + (latency_ms * 0.1)
            model.last_used = datetime.now().isoformat()
            self._save_models()
        
        self._request_history.append({
            "model_id": model_id,
            "success": success,
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat()
        })
    
    def update_quality_score(self, model_id: str, score: float) -> None:
        """Update model quality score"""
        if model_id in self._models:
            self._models[model_id].quality_score = max(0.0, min(1.0, score))
            self._save_models()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics"""
        total_models = len(self._models)
        active_models = sum(1 for m in self._models.values() if m.is_active)
        total_requests = sum(m.total_requests for m in self._models.values())
        total_successful = sum(m.successful_requests for m in self._models.values())
        
        return {
            "total_models": total_models,
            "active_models": active_models,
            "total_requests": total_requests,
            "total_successful": total_successful,
            "overall_success_rate": total_successful / total_requests if total_requests > 0 else 0.0,
            "models": [m.to_dict() for m in self._models.values()]
        }


def init_router(config_path: str = "configs/models.json") -> ModelRouter:
    """Initialize model router"""
    router = ModelRouter(config_path)
    return router
