from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from backend.app.core.config import settings
from backend.app.services.file_processor import process_file
from backend.app.schemas.file import FileResponse, FileInfo
import aiofiles
import numpy as np
from datetime import datetime
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema.document import Document


# Create a singleton embedding model to avoid recreating it for each request
_embedding_model = None
router = APIRouter()


def get_embedding_model():
    """
    Returns a singleton instance of a multilingual embedding model that supports many languages.
    """
    global _embedding_model
    if _embedding_model is None:
        # Use a multilingual model that supports 50+ languages
        _embedding_model = HuggingFaceEmbeddings(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _embedding_model


# Process text into documents with consistent chunking
async def process_text_to_documents(text, metadata=None):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=4000,
        chunk_overlap=400,
        length_function=len
    )

    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk, metadata=metadata or {}) for chunk in chunks]
    return documents
async def convert_text_to_vector(extracted_text, filename=None):
    # Process text into documents with source metadata
    metadata = {"source": filename} if filename else {}
    documents = await process_text_to_documents(extracted_text, metadata)

    # Get embedding model
    embedding_model = get_embedding_model()

    # Create or update vector database with Chroma
    chroma_dir = os.path.join(settings.UPLOAD_DIR, "chroma_db")
    os.makedirs(chroma_dir, exist_ok=True)

    # Create or load vector database
    try:
        vector_db = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embedding_model
        )

        # Add documents to the database
        vector_db.add_documents(documents)
    except Exception as e:
        # If loading fails, create a new database
        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=chroma_dir
        )

    # Persist the database to disk
    vector_db.persist()

    # Return success message
    return f"Added {len(documents)} chunks to vector database".encode()


@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a document file (DOCX, XLSX, etc.)
    """
    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )

    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    try:
        # Use aiofiles to write file asynchronously
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Process file and extract text
        extracted_text = await process_file(file_path, file_extension)

        # Write extracted_text to text file in uploads folder
        text_file_path = os.path.join(settings.UPLOAD_DIR, os.path.splitext(file.filename)[0] + ".txt")
        async with aiofiles.open(text_file_path, "w") as text_file:
            await text_file.write(extracted_text)

        # Add to vector database instead of saving vector file
        result = await convert_text_to_vector(extracted_text, file.filename)
        print(result.decode())

        return FileResponse(
            filename=file.filename,
            content_type=file.content_type,
            text_content=extracted_text
        )
    except Exception as e:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(e)}"
        )

@router.get("/files", response_model=List[FileInfo])
async def list_files():
    """
    Get list of uploaded files
    """
    files = []
    try:
        try:
            os.listdir(settings.UPLOAD_DIR)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Could not list files: {str(e)}"
            )
        for filename in os.listdir(settings.UPLOAD_DIR):
            if ".pdf" not in filename:
                continue
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            stats = os.stat(file_path)
            files.append(FileInfo(
                filename=filename,
                size=stats.st_size,
                uploaded_at=datetime.fromtimestamp(stats.st_mtime)
            ))
        return sorted(files, key=lambda x: x.uploaded_at, reverse=True)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not list files: {str(e)}"
        ) 