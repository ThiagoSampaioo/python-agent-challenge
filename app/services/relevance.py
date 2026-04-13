from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from app.services.kb_parser import KBSection


@dataclass
class RankedSection:
    section: str
    content: str
    score: int


class RelevanceService:
    def __init__(self) -> None:
        self.stopwords = {
            "a", "o", "e", "de", "da", "do", "das", "dos", "em", "na", "no",
            "nas", "nos", "para", "por", "com", "sem", "um", "uma", "uns",
            "umas", "que", "como", "qual", "quais", "quando", "onde", "porque",
            "ser", "é", "ao", "à", "as", "os", "se", "sua", "seu", "suas",
            "seus", "mais", "menos", "deve", "dever", "isso", "esse", "essa",
            "anterior", "falamos", "resposta", "pode", "resumir", "frase",
            "usar"
        }

    def rank_sections(
        self,
        query: str,
        sections: list[KBSection],
        top_k: int = 2,
    ) -> list[RankedSection]:
        query_tokens = self._tokenize(query)
        normalized_query = self._normalize(query)
        ranked: list[RankedSection] = []

        for section in sections:
            score = self._score_section(query_tokens, normalized_query, section)
            if score > 0:
                ranked.append(
                    RankedSection(
                        section=section.section,
                        content=section.content,
                        score=score,
                    )
                )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    def has_sufficient_context(self, ranked_sections: list[RankedSection]) -> bool:
        if not ranked_sections:
            return False

        return ranked_sections[0].score >= 2

    def _score_section(
        self,
        query_tokens: set[str],
        normalized_query: str,
        section: KBSection,
    ) -> int:
        normalized_title = self._normalize(section.section)
        title_tokens = self._tokenize(section.section)
        content_tokens = self._tokenize(section.content)

        score = 0

        if normalized_title and normalized_title in normalized_query:
            score += 12

        title_matches = len(query_tokens & title_tokens)
        content_matches = len(query_tokens & content_tokens)

        score += title_matches * 5
        score += content_matches

        return score

    def _tokenize(self, text: str) -> set[str]:
        normalized = self._normalize(text)
        tokens = re.findall(r"\b[a-z0-9]+\b", normalized)
        return {
            token for token in tokens
            if token not in self.stopwords and len(token) > 1
        }

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFD", text)
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")
        return text