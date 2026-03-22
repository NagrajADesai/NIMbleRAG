from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.src.document_processor import DocumentProcessor
from backend.src.retrieval_engine import RetrievalEngine
from backend.src.vector_manager import VectorStoreManager

router = APIRouter()
vector_manager = VectorStoreManager()
doc_processor = DocumentProcessor()
retrieval_engine = RetrievalEngine()

class FileWrapper:
    """Wraps FastAPI UploadFile to mimic Streamlit's UploadedFile interface for DocumentProcessor."""
    def __init__(self, upload_file: UploadFile):
        self.upload_file = upload_file
        self.name = upload_file.filename
        self.size = upload_file.size or 0
        
    def read(self):
        self.upload_file.file.seek(0)
        return self.upload_file.file.read()
        
    def seek(self, offset):
        self.upload_file.file.seek(offset)

@router.get("/")
def list_databases():
    dbs = vector_manager.list_dbs()
    return {"databases": dbs}

@router.post("/upload")
def upload_documents(
    db_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        wrapped_files = [FileWrapper(f) for f in files]
        
        raw_docs = doc_processor.process_files(wrapped_files)
        if not raw_docs:
            raise HTTPException(status_code=400, detail="No valid text extracted.")
            
        text_chunks = doc_processor.chunk_documents(raw_docs)
        db_path = vector_manager.create_db_dir(db_name)
        retrieval_engine.initialize_vector_store(text_chunks, save_path=db_path)
        
        logs = doc_processor.logger.logs.copy()
        doc_processor.logger.logs = [] # Reset logs for next request
        
        return {
            "message": f"Successfully updated knowledgebase: {db_name}",
            "chunks_created": len(text_chunks),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
