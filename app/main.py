from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Python Agent Challenge",
    description="API com orquestração de fluxo, tool de conhecimento e LLM.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}