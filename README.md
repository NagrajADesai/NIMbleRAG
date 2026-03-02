# 🧠 NIMbleRAG

**NIMbleRAG** is a production-grade, **agentic** Retrieval-Augmented Generation (RAG) system designed to be "nimble" yet powerful. It leverages **[NVIDIA NIM](https://build.nvidia.com/)** (NVIDIA Inference Microservices) and **LangGraph** to deliver intelligent, transparent, and accurate AI document interaction.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![NVIDIA NIM](https://img.shields.io/badge/AI-NVIDIA%20NIM-green)
![LangChain](https://img.shields.io/badge/Framework-LangGraph-orange)
![LangChain](https://img.shields.io/badge/Framework-LangChain-orange)
![Whisper](https://img.shields.io/badge/Voice-Whisper%20Large%20V3-purple)

---

## 🚀 Why NIMbleRAG?

Standard RAG systems often suffer from high latency and poor retrieval accuracy. **NIMbleRAG** solves this by implementing an **agentic workflow** with a streamlined, low-latency pipeline and transparent reasoning:

1.  **🤖 Agentic Workflow**: Uses LangGraph to orchestrate autonomous agents (Retrieval → Generation)
2.  **🔍 Hybrid Search**: Uses **Qdrant** for native hybrid retrieval (Dense HuggingFace embeddings + Sparse FastEmbed BM25)
3.  **🎯 Cross-Encoder Reranking**: Re-scores retrieved documents using `ms-marco-MiniLM-L6-v2` to eliminate noise
4.  **🎙️ Voice Input**: Speak your questions — transcribed in real-time by **NVIDIA NIM Whisper Large V3** via gRPC
5.  **📊 Transparency**: Every agent decision is logged and visible to users for trust and debugging
6.  **⚡ Low Latency**: Bypasses redundant LLM calls for near-instant time-to-first-token

---

## ✨ Key Features

### 🤖 Agentic Workflow (LangGraph)
-   **Streamlined Execution**: Avoids redundant multi-step LLM calls to prioritize speed
-   **Step-by-Step Reasoning**: Transparent agent thoughts displayed in UI
-   **State Management**: Persistent state across nodes for complex workflows

### 🔬 Advanced Retrieval Pipeline
-   **Hybrid Search**: Native Qdrant retrieval using Dense HuggingFace embeddings + Sparse FastEmbed sparse arrays
-   **Cross-Encoder Reranking**: Top-20 → Top-5 reranking using cross-attention scoring
-   **Smart Chunking**: RecursiveCharacterTextSplitter with 1000-char chunks, 100-char overlap
-   **Metadata Preservation**: Source filenames, page numbers, document types retained

### 🧠 Powered by NVIDIA NIM
-   **LLM**: Meta Llama 3.1 8B Instruct via [NVIDIA NIM](https://build.nvidia.com/)
-   **Low Latency**: Enterprise-grade inference with <2s response times
-   **Temperature Control**: 0.3 for creative yet accurate generation
-   **Token Efficiency**: Max 1024 tokens per generation for fast responses

### 🎙️ Voice Input — NVIDIA NIM Whisper Large V3
-   **Speak Your Questions**: Use the microphone widget in the Chat sidebar — no typing needed
-   **Cloud ASR**: Powered by [`nvidia/whisper-large-v3`](https://build.nvidia.com/nvidia/whisper-large-v3) via gRPC at `grpc.nvcf.nvidia.com:443`
-   **Review & Edit**: Transcript is shown with an editable field before submitting to the agent
-   **Visual Indicator**: Voice messages are marked with 🎙️ *Voice input* in the chat history
-   **Native Streamlit**: Uses `st.audio_input` — no external recorder component or ffmpeg needed

### 📂 Multi-Format Document Support
-   **Supported Formats**: PDF, DOCX, PPTX, XLSX, TXT
-   **Intelligent Parsing**: 
    - PyMuPDF for PDFs (handles complex layouts)
    - python-docx/pptx for Office files
    - pandas + openpyxl for Excel sheets
-   **Logging**: Real-time data engineering logs during ingestion

### 🗂️ Multi-Knowledgebase Management
-   **Isolated Databases**: Create separate Qdrant collections for different projects/domains
-   **Easy Switching**: Select and query specific collections via dropdown
-   **Incremental Updates**: Add new documents to existing collections (automatic merging)
-   **Docker Storage**: Backed to `vector_dbs/` via Docker volume mounts

---

## 🚀 Setup & Installation

### Option 1: Local Development

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd NVIDIA-NIM-PDF-RAG
    ```

2.  **Start Qdrant Vector DataBase**:
    ```bash
    docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/vector_dbs:/qdrant/storage qdrant/qdrant
    ```

3.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment**:
    Create a `.env` file in the root directory. Get your API keys from [build.nvidia.com](https://build.nvidia.com/):
    ```env
    NVIDIA_API_KEY=your_nvidia_api_key_here
    whisper_large_v3=your_whisper_api_key_here
    ```

6.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```
    Access at `http://localhost:8501`

### Option 2: Docker Deployment

1.  **Build the Image**:
    ```bash
    docker build -t nimblerag .
    ```

2.  **Run the Container**:
    ```bash
    docker run -p 8501:8501 --env-file .env nimblerag
    ```
    Access the app at `http://localhost:8501`

---

## 📚 How to Use

### Step 1: Create a Knowledgebase 📂

1. Navigate to **"Creating Knowledgebase"** page in the sidebar
2. Enter a database name (e.g., `Research_Papers_2024`)
3. Upload your documents (PDF, DOCX, PPTX, XLSX, TXT)
4. Click **"Process & Create/Update"**
5. Watch the data engineering pipeline:
   - Document parsing and text extraction
   - Chunking with overlap for context preservation
   - Direct injection to Qdrant Collection (Dense HuggingFace vectors + Sparse FastEmbed keywords)

### Step 2: Chat With Your Data 💬

1. Switch to **"Chat With Data"** page
2. Select your target knowledgebase from the dropdown
3. Ask questions in natural language **or use voice** (see Step 3)
4. View the **agent's reasoning trace**:
   - Documents retrieved
   - Final answer generation
5. Explore **source citations** with page numbers for verification

### Step 3: Use Voice Input 🎙️ *(Optional)*

1. In the **Chat With Data** sidebar, find the **🎙️ Voice Input** panel
2. Click the microphone widget and **speak your question**
3. Wait ~1–2 seconds — Whisper automatically transcribes via NVIDIA cloud gRPC
4. Review the **"You said:"** box — edit the transcript if needed
5. Click **🚀 Submit** to send your spoken question to the RAG agent

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | NVIDIA NIM (Llama 3.1 8B) | Answer generation & agent reasoning |
| **Voice / STT** | NVIDIA NIM Whisper Large V3 | Speech-to-text transcription (gRPC cloud) |
| **Orchestration** | LangGraph + LangChain | Agentic workflow state management |
| **Vector DB** | Qdrant (Docker) | Native Hybrid Search (Dense + Sparse) |
| **Embeddings** | all-MiniLM-L6-v2 | Local sentence embeddings (384-dim, 80MB) |
| **Reranker** | ms-marco-MiniLM-L6-v2 | Cross-encoder relevance scoring |
| **UI** | Streamlit | Interactive multi-page web interface |
| **PDF Parsing** | PyMuPDF (fitz) | Fast, accurate PDF text extraction |
| **Evaluation** | Ragas | RAG-specific quality metrics |

---

## 📂 Project Structure

```text
NVIDIA-NIM-PDF-RAG/
├── app.py                          # Main Landing Page & Navigation
├── pages/
│   ├── 1_Creating_Knowledgebase.py # Admin: Ingest & Index Documents
│   └── 2_Chat_With_Data.py         # Chat: Select DB & Query with Agent
├── src/
│   ├── config.py                   # Centralized Configuration
│   ├── document_processor.py       # Multi-Format Parsing & Chunking
│   ├── retrieval_engine.py         # Hybrid Search & Reranking
│   ├── agent_graph.py              # LangGraph Agentic Workflow
│   ├── vector_manager.py           # Multi-DB Directory Management
│   ├── voice_handler.py            # NVIDIA NIM Whisper gRPC Client
│   ├── llm_chain.py                # LangChain Pipeline Builder
│   ├── evaluation.py               # Ragas Evaluation Script
│   └── utils.py                    # Helper Functions
├── vector_dbs/                     # Storage for Qdrant Vector Indices (Docker Mount)
├── requirements.txt                # Python Dependencies
├── Dockerfile                      # Docker Configuration
└── .env                            # Environment Variables (API Keys)
```

---

## 🎯 Key Design Decisions

1. **Agentic Workflow over Simple Chain**: Provides transparency, flexibility, and quality.
2. **Hybrid Search**: Balances keyword precision with semantic understanding natively in Qdrant.
3. **Local Embeddings**: Zero cost, privacy-preserving, offline-capable chunk encoding.
4. **Multi-Knowledgebase**: Isolated collections prevent cross-contamination.
5. **Cross-Encoder Reranking**: Improves precision at acceptable latency cost (~50ms)
6. **gRPC for Voice**: NVIDIA NIM Whisper uses gRPC (not REST) for ultra-low latency audio transcription


---

## Acknowledgments

- **NVIDIA** for NIM API — Llama 3.1 model access and Whisper Large V3 cloud ASR
- **OpenAI** for the original Whisper model architecture
- **LangChain/LangGraph** for RAG orchestration framework
- **Sentence Transformers** for embedding models
- **Qdrant** for Vector DataBase
- **Streamlit** for rapid UI development

---