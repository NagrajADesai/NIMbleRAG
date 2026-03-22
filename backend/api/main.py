from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import knowledgebase, chat, voice

app = FastAPI(
    title="NIMbleRAG API",
    description="Agentic RAG backend powered by LangGraph and FastApi"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledgebase.router, prefix="/api/v1/knowledgebase", tags=["Knowledgebase"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
