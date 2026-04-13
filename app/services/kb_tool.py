import httpx
from app.core.config import settings


class KnowledgeBaseTool:
    def __init__(self, kb_url: str | None = None, timeout: float = 10.0) -> None:
        self.kb_url = kb_url or settings.kb_url
        self.timeout = timeout

    def fetch_markdown(self) -> str:
        try:
            response = httpx.get(self.kb_url, timeout=self.timeout)
            response.raise_for_status()
            markdown = response.text.strip()

            if not markdown:
                raise ValueError("KB vazia")

            return markdown
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Erro ao buscar KB via HTTP: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Erro ao carregar conteúdo da KB: {exc}") from exc