from pathlib import Path

import pytest

from claude_code_py.builtins.search_tools import FileGlobTool, GrepSearchTool
from claude_code_py.tools.base import ToolContext


@pytest.mark.asyncio
async def test_file_glob_tool_finds_matches(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')", encoding="utf-8")
    result = await FileGlobTool().run(
        FileGlobTool.input_model(pattern="**/*.py", base_path="src"), ToolContext(cwd=tmp_path)
    )
    assert "src/main.py" in result


@pytest.mark.asyncio
async def test_grep_search_tool_finds_lines(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello\nneedle here\nbye\n", encoding="utf-8")
    result = await GrepSearchTool().run(
        GrepSearchTool.input_model(pattern="needle", glob="**/*.md"), ToolContext(cwd=tmp_path)
    )
    assert "README.md:2: needle here" in result
