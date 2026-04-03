from __future__ import annotations

from pathlib import Path

from claude_code_py.skills.base import SkillSpec


class SkillLoader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def discover(self) -> list[SkillSpec]:
        if not self.root.exists():
            return []
        specs: list[SkillSpec] = []
        for skill_file in sorted(self.root.glob("*/SKILL.md")):
            body = skill_file.read_text(encoding="utf-8")
            description = self._description(body)
            specs.append(
                SkillSpec(
                    name=skill_file.parent.name,
                    root=skill_file.parent,
                    description=description,
                    prompts=self._prompts(body),
                    references=sorted(skill_file.parent.glob("references/*")),
                )
            )
        return specs

    def _description(self, body: str) -> str:
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
        return ""

    def _prompts(self, body: str) -> list[str]:
        prompts: list[str] = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("-"):
                prompts.append(stripped.removeprefix("-").strip())
        return prompts[:8]
