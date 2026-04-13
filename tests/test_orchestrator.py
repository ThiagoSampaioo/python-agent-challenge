from app.core.constants import FALLBACK_ANSWER
from app.services.orchestrator import MessageOrchestrator
from app.services.kb_parser import KBSection
from app.services.relevance import RankedSection


class FakeKBTool:
    def fetch_markdown(self) -> str:
        return "fake markdown"


class FakeKBParser:
    def parse_sections(self, markdown: str) -> list[KBSection]:
        return [
            KBSection(
                section="Composição",
                content="Definição Composição é quando uma função ou classe utiliza outra instância.",
            ),
            KBSection(
                section="Tool de conhecimento",
                content="A tool recupera contexto e não responde diretamente ao usuário.",
            ),
        ]


class FakeRelevanceWithContext:
    def rank_sections(self, query: str, sections: list[KBSection], top_k: int = 2):
        return [
            RankedSection(
                section="Composição",
                content="Definição Composição é quando uma função ou classe utiliza outra instância.",
                score=5,
            )
        ]

    def has_sufficient_context(self, ranked_sections) -> bool:
        return True


class FakeRelevanceWithoutContext:
    def rank_sections(self, query: str, sections: list[KBSection], top_k: int = 2):
        return []

    def has_sufficient_context(self, ranked_sections) -> bool:
        return False


class FakeLLMClient:
    def generate_answer(self, question: str, context: str, conversation_history=None) -> str:
        return "Composição é o uso de outra instância para executar parte do trabalho."


def test_orchestrator_returns_fallback_when_no_context():
    orchestrator = MessageOrchestrator()
    orchestrator.kb_tool = FakeKBTool()
    orchestrator.kb_parser = FakeKBParser()
    orchestrator.relevance_service = FakeRelevanceWithoutContext()

    response = orchestrator.handle_message("Pergunta fora do escopo")

    assert response.answer == FALLBACK_ANSWER
    assert response.sources == []


def test_orchestrator_returns_answer_and_sources_when_context_exists():
    orchestrator = MessageOrchestrator()
    orchestrator.kb_tool = FakeKBTool()
    orchestrator.kb_parser = FakeKBParser()
    orchestrator.relevance_service = FakeRelevanceWithContext()
    orchestrator.llm_client = FakeLLMClient()

    response = orchestrator.handle_message("O que é composição?")

    assert "Composição" in response.answer
    assert len(response.sources) == 1
    assert response.sources[0].section == "Composição"


def test_orchestrator_keeps_session_history():
    orchestrator = MessageOrchestrator()
    orchestrator.kb_tool = FakeKBTool()
    orchestrator.kb_parser = FakeKBParser()
    orchestrator.relevance_service = FakeRelevanceWithContext()
    orchestrator.llm_client = FakeLLMClient()

    session_id = "sessao-1"

    orchestrator.handle_message("O que é composição?", session_id=session_id)
    history = orchestrator.memory.get_history(session_id)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_orchestrator_isolates_sessions():
    orchestrator = MessageOrchestrator()
    orchestrator.kb_tool = FakeKBTool()
    orchestrator.kb_parser = FakeKBParser()
    orchestrator.relevance_service = FakeRelevanceWithContext()
    orchestrator.llm_client = FakeLLMClient()

    orchestrator.handle_message("Pergunta 1", session_id="sessao-a")
    orchestrator.handle_message("Pergunta 2", session_id="sessao-b")

    history_a = orchestrator.memory.get_history("sessao-a")
    history_b = orchestrator.memory.get_history("sessao-b")

    assert history_a[0]["content"] == "Pergunta 1"
    assert history_b[0]["content"] == "Pergunta 2"