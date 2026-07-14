"""
LLM Client Wrapper for Ollama API.
Handles sending system prompts, parsing JSON responses, validating against Pydantic models,
and returning ERROR FALLBACK objects if validation fails.

HARD RULES:
1. Never let the LLM do math - only request JSON text output
2. Always validate response against provided Pydantic model
3. On any validation failure, return the specified error_fallback object
4. Never expose raw LLM errors to the UI - catch and sanitize
"""
import json
import httpx
from typing import Type, Optional, Any, Dict
from pydantic import BaseModel, ValidationError, Field, ConfigDict
import logging

logger = logging.getLogger(__name__)


class ErrorFallback(BaseModel):
    """Generic error fallback object returned when LLM or validation fails."""
    error: bool = Field(default=True, description="Flag indicating this is an error response")
    error_message: str = Field(..., description="Sanitized error message")
    recovery_suggestion: Optional[str] = Field(default=None, description="Suggested recovery action")

    model_config = ConfigDict(extra='forbid')


class LLMResponse(BaseModel):
    """Wrapper for successful LLM responses."""
    success: bool = Field(default=True)
    data: BaseModel = Field(..., description="Validated Pydantic model instance")
    raw_response: str = Field(..., description="Raw JSON string from LLM for debugging")
    model_used: str = Field(..., description="Ollama model that generated this response")


class LLMClient:
    """
    Client for Ollama local inference API.
    
    This client enforces strict JSON-only output from LLMs and validates
    every response against a provided Pydantic model. If validation fails,
    it returns a standardized error_fallback object instead of crashing.
    
    SECURITY: All requests go to localhost:11434 (Ollama default). No external
    API calls are permitted.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: float = 120.0):
        """
        Initialize LLM client.
        
        Args:
            base_url: Ollama API base URL (must be localhost for security)
            timeout: Request timeout in seconds (default 120s for large model inference)
        """
        # Security check: enforce localhost binding
        if not base_url.startswith("http://127.0.0.1") and not base_url.startswith("http://localhost"):
            raise ValueError(
                "SECURITY VIOLATION: LLMClient must connect to localhost only. "
                f"Received: {base_url}"
            )
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client session."""
        await self._client.aclose()

    async def generate_json(
        self,
        model: str,
        system_prompt: str,
        user_input: Dict[str, Any],
        output_schema: Type[BaseModel],
        error_fallback_schema: Optional[Type[BaseModel]] = None,
        max_retries: int = 2,
    ) -> LLMResponse | ErrorFallback:
        """
        Generate JSON output from LLM and validate against schema.
        
        Args:
            model: Ollama model name (e.g., "qwen2.5:3b")
            system_prompt: System prompt defining the agent's behavior
            user_input: User input as dictionary (will be JSON-encoded)
            output_schema: Pydantic model to validate the response against
            error_fallback_schema: Optional schema for error fallback object
            max_retries: Number of retry attempts on validation failure
            
        Returns:
            LLMResponse with validated data, or ErrorFallback on failure
            
        HARD RULES:
        1. LLMs ONLY generate JSON text - no prose allowed
        2. Python handles ALL validation via Pydantic
        3. On validation failure, retry up to max_retries times
        4. After all retries fail, return error_fallback object
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_input)}
        ]

        payload = {
            "model": model,
            "messages": messages,
            "format": "json",  # Force JSON output mode in Ollama
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic output
                "top_p": 0.9,
            }
        }

        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                response = await self._client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                raw_content = result.get("message", {}).get("content", "")
                
                # Parse JSON from LLM response
                try:
                    # Try to extract JSON if wrapped in markdown code blocks
                    raw_content = raw_content.strip()
                    if raw_content.startswith("```json"):
                        raw_content = raw_content[7:]
                    if raw_content.endswith("```"):
                        raw_content = raw_content[:-3]
                    raw_content = raw_content.strip()
                    
                    parsed_data = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Attempt {attempt + 1}: LLM returned invalid JSON: {str(e)[:100]}"
                    )
                    last_error = f"Invalid JSON from LLM: {str(e)[:100]}"
                    continue
                
                # Validate against Pydantic schema
                try:
                    validated_data = output_schema.model_validate(parsed_data)
                    return LLMResponse(
                        success=True,
                        data=validated_data,
                        raw_response=raw_content,
                        model_used=model
                    )
                except ValidationError as e:
                    logger.warning(
                        f"Attempt {attempt + 1}: Pydantic validation failed: {str(e)[:100]}"
                    )
                    last_error = f"Schema validation failed: {str(e)[:100]}"
                    continue
                    
            except httpx.HTTPError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {str(e)}")
                last_error = f"HTTP error: {str(e)[:100]}"
                continue
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                last_error = f"Unexpected error: {str(e)[:100]}"
                continue

        # All retries exhausted - return error fallback
        logger.error(f"All {max_retries + 1} attempts failed. Last error: {last_error}")
        
        if error_fallback_schema:
            return error_fallback_schema.model_validate({
                "error": True,
                "error_message": "LLM failed to produce valid output after multiple attempts.",
                "recovery_suggestion": "Please simplify your request or check if Ollama is running."
            })
        
        return ErrorFallback(
            error=True,
            error_message="LLM failed to produce valid output after multiple attempts.",
            recovery_suggestion="Please simplify your request or check if Ollama is running."
        )

    async def check_health(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            response = await self._client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
