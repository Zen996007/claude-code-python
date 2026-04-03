from __future__ import annotations

import os

from claude_code_py.models.runtime import RuntimeConfig
from claude_code_py.providers.base import Provider, ProviderConfig
from claude_code_py.providers.mock import MockProvider
from claude_code_py.providers.openai_compatible import OpenAICompatibleProvider


def build_provider(config: RuntimeConfig) -> Provider:
    provider_name = config.provider
    provider_config = ProviderConfig(
        model=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_base=config.api_base,
        api_key_env=config.api_key_env,
        system_prompt=config.system_prompt,
    )
    if provider_name == "mock":
        return MockProvider(provider_config)
    if provider_name in {"openai", "openai-compatible"}:
        if provider_config.api_key_env and provider_config.api_key_env not in os.environ:
            # Defer hard failure to request time, but keep CLI introspection honest.
            pass
        return OpenAICompatibleProvider(provider_config)
    raise ValueError(f"Unsupported provider: {provider_name}")
