from pydantic import BaseModel, Field, field_validator


class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pergunta do usuário")
    session_id: str | None = Field(
        default=None,
        description="Identificador opcional para manter contexto curto por sessão",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message não pode estar vazia")
        return cleaned


class SourceItem(BaseModel):
    section: str


class MessageResponse(BaseModel):
    answer: str
    sources: list[SourceItem]