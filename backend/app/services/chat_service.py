import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma
from backend.app.core.config import settings
from ..api.endpoints.file_processing import get_embedding_model
from fastapi import HTTPException


# Define the chat request model
class ChatRequest(BaseModel):
    message: str
    context_files: Optional[List[str]] = None


# Define the chat response model
class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []


async def load_vector_db():
    """
    Load the existing Chroma vector database
    """
    chroma_dir = os.path.join(settings.UPLOAD_DIR, "chroma_db")

    if not os.path.exists(chroma_dir):
        raise HTTPException(status_code=404, detail="No documents have been uploaded yet")

    try:
        embedding_model = get_embedding_model()
        vector_db = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embedding_model
        )
        return vector_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load vector database: {str(e)}")


async def find_relevant_context(query: str, k: int = 5) -> List[Document]:
    """
    Find the most semantically relevant context from the vector database

    Args:
        query: The user's question or message
        k: Number of chunks to retrieve

    Returns:
        List of relevant document chunks with their metadata
    """
    try:
        # Load the vector database
        vector_db = await load_vector_db()

        # Search for similar documents
        results = vector_db.similarity_search_with_score(query, k=k)

        # Filter results to only include ones with reasonable similarity scores
        relevant_docs = []
        for doc, score in results:
            # Lower score means higher similarity in Chroma
            if score < 15:  # Adjust this threshold as needed
                relevant_docs.append(doc)

        return relevant_docs
    except Exception as e:
        print(f"Error finding relevant context: {str(e)}")
        return []


def format_context_for_prompt(relevant_docs: List[Document]) -> str:
    """
    Format the retrieved documents into a context string for the prompt
    """
    if not relevant_docs:
        return ""

    formatted_context = "I found the following relevant information:\n\n"

    for i, doc in enumerate(relevant_docs, 1):
        source = doc.metadata.get("source", "Unknown source")
        formatted_context += f"[{i}] From {source}:\n{doc.page_content}\n\n"

    return formatted_context


def generate_response(query: str, context: str) -> str:
    """
    Generate a response based on the query and the relevant context

    In a production application, this would likely call an LLM API
    """
    if not context:
        return "I don't have any relevant information in my database to answer your question."

    # In a real implementation, you would send the query and context to an LLM
    # For now, we'll return a simple response
    return f"Based on the documents I've analyzed, I can provide this information to answer your query: '{query}'\n\n{context}"


async def process_chat_message(message: str, context_files: Optional[List[str]] = None) -> ChatResponse:
    """
    Process a chat message and return a response with relevant information from the vector database

    Args:
        message: The user's message or query
        context_files: Optional list of specific files to search within (not used in vector search)

    Returns:
        A ChatResponse object with the answer and source information
    """
    try:
        # Find the most relevant documents using vector similarity search
        relevant_docs = await find_relevant_context(message)

        # If context_files is provided, filter results
        if context_files:
            relevant_docs = [doc for doc in relevant_docs if doc.metadata.get("source") in context_files]

        # Extract source information for the response
        sources = []
        for doc in relevant_docs:
            source = doc.metadata.get("source", "Unknown")
            if source and source not in [s["name"] for s in sources]:
                sources.append({"name": source, "relevance": "high"})

        # Format context for prompt
        context = format_context_for_prompt(relevant_docs)

        # Generate a response
        response_text = generate_response(message, context)

        # Create and return a ChatResponse object
        return ChatResponse(
            response=response_text,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")


# Example of how to implement the chat endpoint in your router
def create_chat_endpoint(router):
    @router.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """
        Process a chat message and return a response
        """
        response = await process_chat_message(request.message, request.context_files)
        return response  # Return the ChatResponse object directly