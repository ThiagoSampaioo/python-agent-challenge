from fastapi import APIRouter, HTTPException

from app.schemas.message import MessageRequest, MessageResponse
from app.services.orchestrator import MessageOrchestrator

router = APIRouter()
orchestrator = MessageOrchestrator()


@router.post("/messages", response_model=MessageResponse)
def create_message(payload: MessageRequest) -> MessageResponse:
    # Recebe a requisição do cliente e delega o processamento
    # para a camada responsável pela lógica da aplicação.
    try:
        return orchestrator.handle_message(
            message=payload.message,
            session_id=payload.session_id,
        )
    except ValueError as exc:
        # Erros de validação ou dados inválidos retornam 400.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        # Falhas de serviço ou indisponibilidade são tratadas como 503.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        # Qualquer erro não previsto retorna erro interno padrão.
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a mensagem.",
        )