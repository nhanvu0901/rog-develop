import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma
from backend.app.core.config import settings
from ..api.endpoints.file_processing import get_embedding_model
from fastapi import HTTPException
import google.generativeai as genai
from ..services.llm_service import setup_genai
# Define the chat request model
class ChatRequest(BaseModel):
    message: str
    context_files: Optional[List[str]] = None


# Define the chat response model
class ChatResponse(BaseModel):
    response: str



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


async def find_relevant_context(query: str, k: int = 5) -> str:

    try:
        # Load the vector database
        vector_db = await load_vector_db()

        # Search for similar documents
        results = vector_db.similarity_search_with_score(query, k=k)

        relevant_docs = []
        for doc, score in results:
            # Lower score means higher similarity in Chroma
            if score < 15:  # Adjust this threshold as needed
                relevant_docs.append(doc)

        context = "\n\n".join(content.page_content for content in relevant_docs)

        prompt = f"""
            Use the following information to answer the question accurately and comprehensively:

            Context:
            {context}
            Instructions:
1. If the provided context only contains tables, lists, or indexes without substantive information about the question, state that substantive information about the query isn't found in the provided context.
2. If the query subject appears only in tables of contents, reference lists, or similar structural elements without accompanying explanatory content, mention this limitation.
3. If you do find relevant information, provide a complete answer based on the available context.
4. If the query subject isn't mentioned at all in the context, clearly state "The information about [query] is not found in the provided context."
            Question: {query}

            Answer:
            """

        return prompt
    except Exception as e:
        print(f"Error finding relevant context: {str(e)}")
        return []





def generate_response(query: str, context: str) -> str:
    model = setup_genai()
    response = model.generate_content(context)
    return response.text


async def process_chat_message(message: str, context_files: Optional[List[str]] = None) -> ChatResponse:

    try:
        prompt = await find_relevant_context(message)

        print(prompt)
        # if context_files:
        #     relevant_docs = [doc for doc in relevant_docs if doc.metadata.get("source") in context_files]
        #
        #
        # sources = []
        # for doc in relevant_docs:
        #     source = doc.metadata.get("source", "Unknown")
        #     sources.append({"name": source})

        response_text = generate_response(message, prompt)
        print(response_text)
        # Create and return a ChatResponse object
        return ChatResponse(
            response=response_text,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")
