from claude_code_py.builtins.file_tools import FileReadTool
from claude_code_py.tools.registry import ToolRegistry


def test_registry_register_and_get() -> None:
    registry = ToolRegistry()
    tool = FileReadTool()
    registry.register(tool)
    assert registry.get("file_read") is tool
    assert "file_read" in registry.names()
