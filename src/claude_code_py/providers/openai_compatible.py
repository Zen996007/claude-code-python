from __future__ import annotations

import os
from typing import Any

import httpx

from claude_code_py.models.messages import AgentResponse, Message, ToolCall
from claude_code_py.providers.base import Provider, ProviderConfig


class OpenAICompatibleProvider(Provider):
    def __init__(self, config: ProviderConfig) -> None:
        if not config.api_base:
            raise ValueError("api_base is required for OpenAICompatibleProvider")
        if not config.api_key_env:
            raise ValueError("api_key_env is required for OpenAICompatibleProvider")
        self.config = config

    async def generate(self, messages: list[Message], *, tools: list[dict] | None = None) -> AgentResponse:
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing provider API key env var: {self.config.api_key_env}")

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [self._message_to_wire(message) for message in messages],
            "temperature": self.config.temperature,
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": tool} for tool in tools]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **self.config.extra_headers,
        }

        async with httpx.AsyncClient(base_url=self.config.api_base, timeout=60.0) as client:
            response = await client.post("/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return self._parse_response(data)

    def _message_to_wire(self, message: Message) -> dict[str, Any]:
        payload = {"role": message.role, "content": message.content}
        if message.name:
            payload["name"] = message.name
        return payload

    def _parse_response(self, data: dict[str, Any]) -> AgentResponse:
        choice = data["choices"][0]["message"]
        tool_calls = []
        for item in choice.get("tool_calls", []):
            function = item.get("function", {})
            tool_calls.append(
                ToolCall(
                    id=item.get("id"),
                    name=function.get("name", "unknown"),
                    arguments=self._safe_json_load(function.get("arguments", "{}")),
                )
            )
        text = choice.get("content") or ""
        stop_reason = "tool_use" if tool_calls else "end_turn"
        return AgentResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            metadata={"provider": "openai-compatible"},
        )

    def _safe_json_load(self, raw: str) -> dict[str, Any]:
        import json

        parsed = json.loads(raw or "{}")
        if not isinstance(parsed, dict):
            raise ValueError("Tool arguments must decode to a JSON object")
        return parsed
