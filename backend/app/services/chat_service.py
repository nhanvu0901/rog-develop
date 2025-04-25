import os
from backend.app.core.config import settings
import numpy as np
from typing import List, Optional
from ..api.endpoints.file_processing import convert_text_to_vector
async def load_context_from_file(file_path: str) -> str:
    """
    Load and return the content of a text file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        return ""

async def find_relevant_context(message: str, context_files: Optional[List[str]] = None, ext: str = ".txt") -> str:
    """
    Find relevant context from uploaded files for the query
    """
    all_context = ""

    # If specific files are provided, use only those
    if context_files:
        for filename in context_files:
            file_path = os.path.join(settings.UPLOAD_DIR, filename + ext)
            if os.path.exists(file_path):
                content = await load_context_from_file(file_path)

                # TODO: TEST - find the context that is most relevant to the message
                if message in content:
                    all_context = content
                    break

                # all_context += content + "\n\n"
    else:
        # Otherwise, search through all uploaded files
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith(".txt"):
                content = await load_context_from_file(os.path.join(settings.UPLOAD_DIR, filename))

                # TODO: TEST - find the context that is most relevant to the message
                if message in content:
                    all_context = content
                    break

                # all_context += content + "\n\n"

    return all_context


async def find_most_relevant_context(input_message):
    message_vector = await convert_text_to_vector(input_message)
    vector_data = [vector_data for vector_data in os.listdir(settings.UPLOAD_DIR) if vector_data.endswith(".vector")]
    print(vector_data)

async def process_chat_message(message: str, context_files: Optional[List[str]] = None) -> str:
    """
    Process a chat message and return a response
    """
    try:
        # Get relevant context from uploaded files. extension is .vector


        context = await find_relevant_context(message, context_files, ".txt")

        # For now, return a simple response
        # TODO: Implement actual chat processing logic
        if context:
            return f"I found some relevant information from the uploaded files: {context[:200]}..."
        else:
            return "I don't have any relevant information from the uploaded files to answer your question."

    except Exception as e:
        raise Exception(f"Error processing chat message: {str(e)}")