import pytest

from claude_code_py.models.messages import Message
from claude_code_py.providers.base import ProviderConfig
from claude_code_py.providers.mock import MockProvider
from claude_code_py.providers.openai_compatible import OpenAICompatibleProvider


@pytest.mark.asyncio
async def test_mock_provider_returns_text() -> None:
    provider = MockProvider()
    response = await provider.generate([Message(role="user", content="hello")])
    assert response.text == "MockProvider: hello"


def test_openai_compatible_requires_config() -> None:
    with pytest.raises(ValueError):
        OpenAICompatibleProvider(ProviderConfig())
