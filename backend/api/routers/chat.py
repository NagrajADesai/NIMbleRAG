from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.src.vector_manager import VectorStoreManager
from backend.src.retrieval_engine import RetrievalEngine
from backend.src.agent_graph import build_graph

router = APIRouter()
vector_manager = VectorStoreManager()
retrieval_engine = RetrievalEngine()

class ChatRequest(BaseModel):
    query: str
    database_name: str

@router.post("/query")
def chat_query(request: ChatRequest):
    dbs = vector_manager.list_dbs()
    if request.database_name not in dbs:
         raise HTTPException(status_code=404, detail="Database not found")
         
    try:
        db_path = vector_manager.get_db_path(request.database_name)
        retrieval_engine.initialize_vector_store(text_chunks=None, save_path=db_path)
        retriever = retrieval_engine.get_hybrid_retriever()
        agent_app = build_graph(retriever)
        
        inputs = {"question": request.query}
        final_state = agent_app.invoke(inputs)
        
        answer_text = final_state.get("generation", "I couldn't generate an answer.")
        source_docs = final_state.get("documents", [])
        steps = final_state.get("steps", [])
        
        sources_formatted = []
        for doc in source_docs:
             sources_formatted.append({
                 "source": doc.metadata.get('source', 'Unknown'),
                 "page": doc.metadata.get('page', 'Unknown'),
                 "content": doc.page_content[:200]
             })
             
        return {
            "answer": answer_text,
            "steps": steps,
            "sources": sources_formatted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
