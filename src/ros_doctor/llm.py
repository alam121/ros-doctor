from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_MODEL = os.environ.get("ROS_DOCTOR_MODEL", "gpt-5-mini")


@dataclass(frozen=True)
class LLMResult:
    text: str
    raw: dict[str, Any]


class LLMUnavailable(RuntimeError):
    pass


def call_openai_response(prompt: str, model: str = DEFAULT_MODEL) -> LLMResult:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMUnavailable("OPENAI_API_KEY is not set.")

    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMUnavailable(f"OpenAI API request failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise LLMUnavailable(f"OpenAI API request failed: {exc}") from exc

    return LLMResult(text=_extract_output_text(raw), raw=raw)


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"LLM response did not contain a JSON object: {text[:200]}")
    return json.loads(stripped[start : end + 1])


def _extract_output_text(raw: dict[str, Any]) -> str:
    if isinstance(raw.get("output_text"), str):
        return raw["output_text"]

    chunks: list[str] = []
    for item in raw.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks)
