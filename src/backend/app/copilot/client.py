from __future__ import annotations

import json
from functools import lru_cache
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings


class LlmProviderUnavailable(RuntimeError):
    pass


class LlmRequestFailed(RuntimeError):
    pass


class LlmClient:
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        settings = get_settings()
        if not settings.llm_enabled:
            raise LlmProviderUnavailable("LLM provider is not configured")

        endpoint = settings.llm_api_base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = f"{endpoint}/chat/completions"

        body = json.dumps(
            {
                "model": settings.llm_model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        ).encode("utf-8")
        request = Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.llm_api_key}",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise LlmRequestFailed(f"LLM request failed with status {exc.code}") from exc
        except URLError as exc:
            raise LlmRequestFailed("LLM request could not reach the provider") from exc

        try:
            raw_content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmRequestFailed("LLM response did not contain a chat completion") from exc
        content = self._flatten_content(raw_content)
        return self._parse_json_payload(content)

    def _flatten_content(self, content: object) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            return "\n".join(parts)
        return ""

    def _parse_json_payload(self, content: str) -> dict[str, Any]:
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return {"answer": content.strip(), "follow_up_questions": []}
            parsed = json.loads(content[start : end + 1])
        if not isinstance(parsed, dict):
            return {"answer": content.strip(), "follow_up_questions": []}
        return parsed


@lru_cache
def get_llm_client() -> LlmClient:
    return LlmClient()
