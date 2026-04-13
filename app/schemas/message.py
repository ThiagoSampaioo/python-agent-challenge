from pydantic import BaseModel, Field, field_validator


class MessageRequest(BaseModel):
    # Mensagem enviada pelo usuário
    message: str = Field(..., min_length=1, description="Pergunta do usuário")

    # Id opcional para manter um pequeno contexto por sessão
    session_id: str | None = Field(
        default=None,
        description="Identificador opcional para manter contexto curto por sessão",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        # Remove espaços extras antes de validar
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message não pode estar vazia")
        return cleaned


class SourceItem(BaseModel):
    # Seção da base usada como referência na resposta
    section: str


class MessageResponse(BaseModel):
    # Texto final retornado para o usuário
    answer: str

    # Lista de seções usadas como fonte
    sources: list[SourceItem]