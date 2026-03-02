from typing import List, Annotated, Dict, TypedDict, Any
from langgraph.graph import StateGraph, END

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain.docstore.document import Document
from src.config import ModelConfig
import json

# --- State Definition ---
class AgentState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    steps: List[str]  # Trace of agent thoughts

# --- Nodes ---

class AgentNodes:
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = ChatNVIDIA(
            base_url=ModelConfig.NVIDIA_BASE_URL,
            model_name=ModelConfig.LLM_MODEL,
            temperature=0, # Low temp for reasoning
            max_tokens=1024,
        )
        self.gen_llm = ChatNVIDIA(
            base_url=ModelConfig.NVIDIA_BASE_URL,
            model_name=ModelConfig.LLM_MODEL,
            temperature=0.3, # Slight creep for generation
            max_tokens=1024,
        )

    def retrieve(self, state: AgentState):
        """
        Retrieve documents from vector store.
        """
        question = state["question"]
        steps = state.get("steps", [])
        steps.append("Retrieving documents from Vector DB...")
        
        # Retrieval
        documents = self.retriever.invoke(question)
        
        steps.append(f"Retrieved {len(documents)} documents.")
        return {"documents": documents, "question": question, "steps": steps}

    def generate(self, state: AgentState):
        """
        Generate answer.
        """
        question = state["question"]
        documents = state["documents"]
        steps = state.get("steps", [])
        steps.append("Generating final answer...")

        # Generator Prompt
        prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. \n
            If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise. \n
            
            Question: {question} \n
            Context: {context} \n
            
            Answer:""",
            input_variables=["question", "context"],
        )
        
        # Format context
        context = "\n\n".join([d.page_content for d in documents])
        
        rag_chain = prompt | self.gen_llm | StrOutputParser()
        
        try:
            generation = rag_chain.invoke({"context": context, "question": question})
        except Exception as e:
            generation = f"Error during generation: {e}"
            
        steps.append("Generation complete.")
        return {"documents": documents, "question": question, "generation": generation, "steps": steps}

# --- Graph Construction ---

def build_graph(retriever):
    workflow = StateGraph(AgentState)
    nodes = AgentNodes(retriever)

    # Define Nodes
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("generate", nodes.generate)

    # Define Edges - Straight line pipeline
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    app = workflow.compile()
    return app
