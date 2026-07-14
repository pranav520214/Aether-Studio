"""
Privantrix AI OS - LM Studio Client
Production-grade LM Studio API client with retry logic and streaming
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator, Callable
from dataclasses import dataclass, field
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


@dataclass
class ModelInfo:
    """Information about a loaded model"""
    id: str = ""
    name: str = ""
    context_length: int = 4096
    is_loaded: bool = False
    capabilities: List[str] = field(default_factory=list)


@dataclass
class CompletionResponse:
    """Response from completion request"""
    content: str = ""
    model: str = ""
    finish_reason: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


class LMStudioClient:
    """Client for LM Studio API"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 1234,
        api_base: str = "/v1",
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.host = host
        self.port = port
        self.api_base = api_base
        self.base_url = f"http://{host}:{port}{api_base}"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session = requests.Session()
        self._available_models: List[ModelInfo] = []
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        for attempt in range(self.max_retries):
            try:
                response = self._session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
        
        return None
    
    def health_check(self) -> bool:
        """Check if LM Studio server is available"""
        try:
            response = self._request("GET", "/models")
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    def get_models(self) -> List[ModelInfo]:
        """Get list of available models"""
        try:
            response = self._request("GET", "/models")
            if response:
                data = response.json()
                models = []
                for model_data in data.get("data", []):
                    model = ModelInfo(
                        id=model_data.get("id", ""),
                        name=model_data.get("name", model_data.get("id", "")),
                        is_loaded=True
                    )
                    models.append(model)
                self._available_models = models
                return models
        except Exception:
            pass
        return []
    
    def get_loaded_model(self) -> Optional[ModelInfo]:
        """Get the currently loaded model"""
        models = self.get_models()
        return models[0] if models else None
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 1.0,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0
    ) -> CompletionResponse:
        """Generate chat completion"""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty
        }
        
        if model:
            payload["model"] = model
        
        if stop:
            payload["stop"] = stop
        
        response = self._request(
            "POST",
            "/chat/completions",
            json=payload,
            stream=stream
        )
        
        if not response:
            raise Exception("Failed to get completion response")
        
        if stream:
            # For streaming, we handle it differently
            return self._process_stream_response(response)
        
        data = response.json()
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        return CompletionResponse(
            content=message.get("content", ""),
            model=data.get("model", ""),
            finish_reason=choice.get("finish_reason", ""),
            usage=data.get("usage", {}),
            raw_response=data
        )
    
    def _process_stream_response(
        self,
        response: requests.Response
    ) -> CompletionResponse:
        """Process streaming response"""
        content_parts = []
        model = ""
        finish_reason = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        
                        if delta.get("content"):
                            content_parts.append(delta["content"])
                        
                        if choice.get("finish_reason"):
                            finish_reason = choice["finish_reason"]
                        
                        if data.get("model"):
                            model = data["model"]
                    except json.JSONDecodeError:
                        continue
        
        return CompletionResponse(
            content="".join(content_parts),
            model=model,
            finish_reason=finish_reason,
            raw_response={"streamed": True}
        )
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        on_token: Optional[Callable[[str], None]] = None
    ) -> Generator[str, None, None]:
        """Stream chat completion with callback"""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1.0,
            "stream": True,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
        }
        
        if model:
            payload["model"] = model
        
        response = self._request(
            "POST",
            "/chat/completions",
            json=payload,
            stream=True
        )
        
        if not response:
            raise Exception("Failed to get streaming response")
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        
                        if delta.get("content"):
                            token = delta["content"]
                            if on_token:
                                on_token(token)
                            yield token
                    except json.JSONDecodeError:
                        continue
    
    def generate_embeddings(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embeddings for text"""
        payload = {
            "input": text
        }
        
        if model:
            payload["model"] = model
        
        response = self._request(
            "POST",
            "/embeddings",
            json=payload
        )
        
        if not response:
            raise Exception("Failed to get embeddings")
        
        data = response.json()
        embeddings_data = data.get("data", [])
        
        if embeddings_data:
            return embeddings_data[0].get("embedding", [])
        
        return []
    
    def switch_model(self, model_id: str) -> bool:
        """Switch to a different model (requires LM Studio to support this)"""
        # Note: LM Studio doesn't have a direct API for switching models
        # This would require user interaction in LM Studio
        # We can only verify if the model is available
        models = self.get_models()
        return any(m.id == model_id for m in models)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "host": self.host,
            "port": self.port,
            "base_url": self.base_url,
            "is_available": self.health_check(),
            "models_count": len(self._available_models)
        }


def init_lmstudio_client(
    host: str = "localhost",
    port: int = 1234,
    timeout: int = 120
) -> LMStudioClient:
    """Initialize LM Studio client"""
    client = LMStudioClient(host=host, port=port, timeout=timeout)
    return client


def check_lmstudio_availability(host: str = "localhost", port: int = 1234) -> bool:
    """Check if LM Studio is available"""
    client = LMStudioClient(host=host, port=port)
    return client.health_check()
