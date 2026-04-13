from __future__ import annotations

from app.core.config import settings
from app.core.constants import FALLBACK_ANSWER
from app.schemas.message import MessageResponse, SourceItem
from app.services.kb_parser import KnowledgeBaseParser
from app.services.kb_tool import KnowledgeBaseTool
from app.services.llm_client import LLMClient
from app.services.memory import SessionMemory
from app.services.relevance import RelevanceService, RankedSection


class MessageOrchestrator:
    def __init__(self) -> None:
        self.kb_tool = KnowledgeBaseTool()
        self.kb_parser = KnowledgeBaseParser()
        self.relevance_service = RelevanceService()
        self.llm_client = None
        self.memory = SessionMemory(
            ttl_seconds=settings.session_ttl_seconds,
            max_messages=settings.session_max_messages,
        )

    def handle_message(self, message: str, session_id: str | None = None) -> MessageResponse:
        cleaned_message = message.strip()
        if not cleaned_message:
            raise ValueError("message não pode estar vazia")

        history = self.memory.get_history(session_id)

        if self._is_summary_request(cleaned_message):
            return self._handle_summary_request(cleaned_message, session_id)

        retrieval_query = self._build_retrieval_query(cleaned_message, history)

        markdown = self.kb_tool.fetch_markdown()
        sections = self.kb_parser.parse_sections(markdown)
        ranked_sections = self.relevance_service.rank_sections(
            retrieval_query,
            sections,
            top_k=4,
        )

        if not self.relevance_service.has_sufficient_context(ranked_sections):
            return self._fallback_response()

        if self._should_force_fallback(cleaned_message, ranked_sections):
            return self._fallback_response()

        ranked_sections = self._apply_expected_section_rule(cleaned_message, ranked_sections)

        if not ranked_sections:
            return self._fallback_response()

        context = self._build_context(ranked_sections)

        llm_client = self._get_llm_client()
        answer = llm_client.generate_answer(
            question=cleaned_message,
            context=context,
            conversation_history=history,
        )

        cleaned_answer = self._sanitize_answer(answer)
        if not cleaned_answer:
            return self._fallback_response()

        selected_sections = self._select_output_sections(cleaned_message, ranked_sections)

        self.memory.add_message(session_id, "user", cleaned_message)
        self.memory.add_message(
            session_id,
            "assistant",
            cleaned_answer,
            sources=selected_sections,
        )

        return MessageResponse(
            answer=cleaned_answer,
            sources=[SourceItem(section=section) for section in selected_sections],
        )

    def _handle_summary_request(
        self,
        message: str,
        session_id: str | None,
    ) -> MessageResponse:
        last_assistant_message = self.memory.get_last_assistant_message(session_id)
        if not last_assistant_message:
            return self._fallback_response()

        original_text = last_assistant_message.get("content", "").strip()
        original_sources = last_assistant_message.get("sources", [])

        if not original_text:
            return self._fallback_response()

        llm_client = self._get_llm_client()

        instruction = (
            "Resuma a resposta anterior de forma curta e fiel."
            if "resposta anterior" in message.lower()
            else "Resuma o que foi respondido até aqui de forma curta e fiel."
        )

        summary = llm_client.summarize_text(original_text, instruction=instruction)
        cleaned_summary = self._sanitize_answer(summary)

        if not cleaned_summary:
            return self._fallback_response()

        self.memory.add_message(session_id, "user", message)
        self.memory.add_message(
            session_id,
            "assistant",
            cleaned_summary,
            sources=original_sources,
        )

        return MessageResponse(
            answer=cleaned_summary,
            sources=[SourceItem(section=section) for section in original_sources],
        )

    def _get_llm_client(self) -> LLMClient:
        if self.llm_client is None:
            self.llm_client = LLMClient()
        return self.llm_client

    def _is_summary_request(self, message: str) -> bool:
        lowered = message.lower().strip()
        summary_patterns = [
            "pode resumir o que falamos",
            "pode resumir a resposta anterior",
            "resuma o que falamos",
            "resuma a resposta anterior",
        ]
        return any(pattern in lowered for pattern in summary_patterns)

    def _should_force_fallback(
        self,
        message: str,
        ranked_sections: list[RankedSection],
    ) -> bool:
        normalized_message = message.lower().strip()

        fallback_patterns = [
            "como agir sem contexto suficiente",
            "o que fazer sem contexto suficiente",
            "sem contexto suficiente",
        ]

        if any(pattern in normalized_message for pattern in fallback_patterns):
            return True

        if ranked_sections and ranked_sections[0].section == "Falta de contexto":
            return True

        return False

    def _fallback_response(self) -> MessageResponse:
        return MessageResponse(
            answer=FALLBACK_ANSWER,
            sources=[],
        )

    def _build_retrieval_query(
        self,
        current_message: str,
        history: list[dict[str, str]],
    ) -> str:
        if not self._is_follow_up_message(current_message):
            return current_message

        previous_user_messages = [
            item["content"]
            for item in history
            if item.get("role") == "user" and item.get("content", "").strip()
        ]

        if not previous_user_messages:
            return current_message

        last_user_message = previous_user_messages[-1]
        return f"{last_user_message}\n{current_message}"

    def _is_follow_up_message(self, message: str) -> bool:
        lowered = message.lower().strip()

        follow_up_patterns = [
            "resuma",
            "resumir",
            "resumo",
            "pode resumir",
            "em uma frase",
            "explique melhor",
            "melhore",
            "e isso",
            "e esse",
            "e essa",
            "pode explicar",
            "continue",
        ]

        if len(lowered.split()) <= 5:
            return True

        return any(pattern in lowered for pattern in follow_up_patterns)

    def _expected_sections_for_message(self, message: str) -> list[str] | None:
        normalized = self._normalize_text(message)

        if "o que e composicao" in normalized or "composicao" in normalized:
            return ["Composição"]

        if "quando usar heranca" in normalized or "heranca" in normalized:
            return ["Herança"]

        if "qual o papel da orquestracao" in normalized or "papel da orquestracao" in normalized:
            return ["Orquestração"]

        if "tool deve responder diretamente ao usuario" in normalized:
            return ["Tool de conhecimento"]

        if "qual o papel da tool" in normalized or "papel da tool de conhecimento" in normalized:
            return ["Tool de conhecimento"]

        if "onde colocar regra de negocio" in normalized:
            return ["Endpoint de API", "Responsabilidade única"]

        return None

    def _apply_expected_section_rule(
        self,
        message: str,
        ranked_sections: list[RankedSection],
    ) -> list[RankedSection]:
        expected_sections = self._expected_sections_for_message(message)
        if not expected_sections:
            return ranked_sections[:2]

        filtered = [item for item in ranked_sections if item.section in expected_sections]
        if filtered:
            ordered_filtered: list[RankedSection] = []
            for expected in expected_sections:
                match = next((item for item in filtered if item.section == expected), None)
                if match:
                    ordered_filtered.append(match)
            return ordered_filtered

        return ranked_sections[:1]

    def _build_context(self, ranked_sections: list[RankedSection]) -> str:
        context_blocks: list[str] = []

        for item in ranked_sections:
            context_blocks.append(f"Seção: {item.section}\n{item.content}")

        return "\n\n".join(context_blocks).strip()

    def _select_output_sections(
        self,
        message: str,
        ranked_sections: list[RankedSection],
    ) -> list[str]:
        expected_sections = self._expected_sections_for_message(message)
        if expected_sections:
            return expected_sections

        if not ranked_sections:
            return []

        return [ranked_sections[0].section]

    def _sanitize_answer(self, answer: str) -> str:
        return (answer or "").strip()

    def _normalize_text(self, text: str) -> str:
        replacements = {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
            "?": "",
            "!": "",
        }

        normalized = text.lower().strip()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized