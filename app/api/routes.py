from fastapi import APIRouter, HTTPException

from app.schemas.message import MessageRequest, MessageResponse
from app.services.orchestrator import MessageOrchestrator

router = APIRouter()
orchestrator = MessageOrchestrator()


@router.post("/messages", response_model=MessageResponse)
def create_message(payload: MessageRequest) -> MessageResponse:
    try:
        return orchestrator.handle_message(
            message=payload.message,
            session_id=payload.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a mensagem.",
        )