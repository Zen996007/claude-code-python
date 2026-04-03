import pytest

from claude_code_py.models.messages import Message
from claude_code_py.providers.mock import MockProvider


@pytest.mark.asyncio
async def test_mock_provider_stream_emits_events() -> None:
    provider = MockProvider()
    events = [event async for event in provider.stream([Message(role="user", content="hello world")])]
    assert events[0].type == "response.started"
    assert any(event.type == "response.delta" for event in events)
    assert events[-1].type == "response.completed"
