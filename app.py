import streamlit as st
import nest_asyncio
nest_asyncio.apply()
from src.config import AppConfig

def main():
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        page_icon=AppConfig.APP_ICON,
        layout=AppConfig.LAYOUT
    )

    st.title("🧠 NIMbleRAG: Agentic RAG System")

    st.markdown("""
    ### 🚀 Production-Grade Intelligent Document Q&A

    **NIMbleRAG** transforms static documents into an **intelligent, queryable knowledge base** using an **agentic workflow** powered by LangGraph.
    Unlike traditional RAG systems, NIMbleRAG employs autonomous agents that intelligently route, retrieve, grade, and generate answers with transparency.
    Now with **🎙️ Voice Input** — speak your questions and let NVIDIA NIM Whisper transcribe them instantly.

    ---

    ## 🤖 Agentic Workflow Architecture

    The system uses **LangGraph** to orchestrate a multi-node decision pipeline:

    ```
    Voice / Text → Router Agent → Retrieval Agent → Grader Agent → Generator Agent → Answer
    ```

    - **🎙️ Voice Input**: Speak questions — transcribed by NVIDIA NIM Whisper Large V3 (gRPC cloud)
    - **🧭 Router Agent**: Intelligently classifies queries (RAG vs. general chat)
    - **🔍 Retrieval Agent**: Fetches documents using hybrid search (BM25 + FAISS)
    - **⚖️ Grader Agent**: LLM-based relevance filtering to eliminate noise
    - **✍️ Generator Agent**: Context-aware answer generation with citations
    - **📊 Transparency**: Every step is logged and visible to users

    ---

    ## ✨ Key Features

    ### 🎙️ Voice Input — NVIDIA NIM Whisper Large V3
    -   **Speak Your Questions**: Click the mic in the Chat sidebar and ask anything — no typing needed
    -   **Real-Time Transcription**: Powered by `nvidia/whisper-large-v3` via the Riva gRPC cloud API
    -   **Review Before Submitting**: Transcript shown in an editable box so you can correct before sending
    -   **Voice Badge in Chat**: Messages from voice input are marked with 🎙️ *Voice input*

    ### 🔬 Advanced Retrieval Pipeline
    -   **Hybrid Search**: Combines **BM25** (keyword precision) + **FAISS** (semantic understanding)
    -   **Cross-Encoder Reranking**: `ms-marco-MiniLM-L6-v2` re-scores top-20 → top-5 documents
    -   **Context Construction**: Smart chunking with 1000-char windows and 100-char overlap

    ### 🧠 Powered by NVIDIA NIM
    -   **LLM**: Meta Llama 3.1 8B Instruct via [NVIDIA NIM](https://build.nvidia.com/)
    -   **Voice ASR**: Whisper Large V3 via NVIDIA NIM gRPC endpoint
    -   **Low Latency**: Enterprise-grade inference with <2s response times
    -   **Consistent Reasoning**: Temperature-controlled for routing (0.0) and generation (0.3)

    ### 📂 Multi-Format Support
    -   **Supported Formats**: PDF, DOCX, PPTX, XLSX, TXT
    -   **Intelligent Parsing**: PyMuPDF for PDFs, python-docx/pptx for Office files
    -   **Metadata Preservation**: Source filenames, page numbers, document types

    ### 🗂️ Multi-Knowledgebase Management
    -   **Isolated Databases**: Create separate knowledge bases for different projects
    -   **Easy Switching**: Select and query specific databases on-the-fly
    -   **Incremental Updates**: Add documents to existing databases seamlessly

    ### 🔬 Built-in Evaluation
    -   **Ragas Metrics**: Faithfulness, answer relevance, context precision
    -   **Quality Assurance**: Validate RAG performance with industry-standard metrics

    ---

    ## 📚 How to Use

    ### Step 1: Create a Knowledgebase 📂
    1. Navigate to **"Creating Knowledgebase"** in the sidebar
    2. Enter a database name (e.g., "Research_Papers_2024")
    3. Upload your documents (PDF, DOCX, PPTX, XLSX, TXT)
    4. Watch the data engineering pipeline process your files:
       - Document parsing and text extraction
       - Chunking with overlap for context preservation
       - Dual indexing (FAISS vectors + BM25 keywords)

    ### Step 2: Chat With Your Data 💬
    1. Switch to **"Chat With Data"** page
    2. Select your target knowledgebase from the dropdown
    3. Ask questions by typing **or use voice** (see below)
    4. View the **agent's reasoning trace**:
       - Query routing decision
       - Documents retrieved and graded
       - Final answer generation
    5. Explore **source citations** with page numbers for verification

    ### Step 3: Voice Input 🎙️
    1. In the **Chat With Data** sidebar, find the **🎙️ Voice Input** panel
    2. Click the microphone and **speak your question**
    3. Whisper transcribes it automatically via the NVIDIA cloud
    4. Review the **"You said:"** box — edit if needed
    5. Click **🚀 Submit** — your voice question is sent to the RAG agent

    ---

    ## 🏗️ System Architecture

    **NIMbleRAG** implements a **4-layer architecture**:

    1. **Presentation Layer**: Streamlit multi-page UI
    2. **Application Layer**: LangGraph agent orchestration
    3. **Business Logic**: Retrieval engine, document processor, vector manager, voice handler
    4. **Data Layer**: FAISS vector stores, BM25 indices, local embeddings

    *Built with ❤️ using LangGraph, LangChain, FAISS, Streamlit, and NVIDIA AI Endpoints — including Whisper Large V3 for voice.*
    """)

if __name__ == "__main__":
    main()