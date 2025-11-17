from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory or current directory
env_path = Path(__file__).parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)
load_dotenv()  # Also try current directory

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")


class GroqAPIError(RuntimeError):
    pass


class GroqClient:
    def __init__(self) -> None:
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.base_url = GROQ_BASE_URL

    async def chat_completion(
        self,
        messages: List[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 900,
        response_format: Optional[str] = None,
    ) -> str:
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set. Running in fallback mode.")
            return self._fallback_response(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format == "json_schema":
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)

            if response.status_code >= 400:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise GroqAPIError(error_msg)

            data = response.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as exc:
                error_msg = f"Unexpected Groq response format: {json.dumps(data)}"
                logger.error(error_msg)
                raise GroqAPIError(error_msg) from exc
        except httpx.TimeoutException as exc:
            error_msg = f"Groq API timeout: {str(exc)}"
            logger.error(error_msg)
            raise GroqAPIError(error_msg) from exc
        except httpx.RequestError as exc:
            error_msg = f"Groq API connection error: {str(exc)}"
            logger.error(error_msg)
            raise GroqAPIError(error_msg) from exc

    def _fallback_response(self, messages: List[dict[str, str]]) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "No prompt provided.")
        return (
            "Groq API key not configured. Running in offline fallback mode.\n\n"
            "Last user prompt:\n"
            f"{last_user}\n\n"
            "Please configure GROQ_API_KEY to enable live analysis."
        )


groq_client = GroqClient()

