from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class KBSection:
    section: str
    content: str


class KnowledgeBaseParser:
    def parse_sections(self, markdown: str) -> list[KBSection]:
        lines = [line.strip() for line in markdown.splitlines()]
        sections: list[KBSection] = []

        current_title: str | None = None
        current_lines: list[str] = []

        for raw_line in lines:
            if not raw_line:
                continue

            line = self._clean_heading(raw_line)

            if self._is_section_title(raw_line, line):
                if current_title:
                    sections.append(
                        KBSection(
                            section=current_title,
                            content="\n".join(current_lines).strip(),
                        )
                    )

                current_title = line
                current_lines = []
                continue

            if current_title:
                current_lines.append(line)

        if current_title:
            sections.append(
                KBSection(
                    section=current_title,
                    content="\n".join(current_lines).strip(),
                )
            )

        return sections

    def _clean_heading(self, line: str) -> str:
        return re.sub(r"^#{1,6}\s*", "", line).strip()

    def _is_section_title(self, raw_line: str, cleaned_line: str) -> bool:
        blocked_titles = {
            "Base de Conhecimento — Python Agent Challenge",
            "Definição",
            "Na prática",
            "Quando usar",
            "Observação curta",
            "Ponto de atenção",
        }

        if cleaned_line in blocked_titles:
            return False

        if cleaned_line.startswith("{") or cleaned_line.startswith("["):
            return False

        if len(cleaned_line) > 60:
            return False

        if ":" in cleaned_line:
            return False

        return raw_line.startswith("#")