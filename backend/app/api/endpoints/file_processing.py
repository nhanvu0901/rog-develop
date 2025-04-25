from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from backend.app.core.config import settings
from backend.app.services.file_processor import process_file
from backend.app.schemas.file import FileResponse, FileInfo
import aiofiles
import numpy as np
from datetime import datetime

router = APIRouter()

# Convert text to vector for model. Notes: vector is fit for model
async def convert_text_to_vector(text: str) -> bytes:
    # Simple vectorization using numpy
    vector = np.array([ord(c) for c in text], dtype=np.float32)
    return vector.tobytes()

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
        # Sử dụng aiofiles để ghi file bất đồng bộ
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Process file and extract text
        extracted_text = await process_file(file_path, file_extension)
        
        # write extracted_text to text file in uploads folder
        text_file_path = os.path.join(settings.UPLOAD_DIR, file.filename + ".txt")
        async with aiofiles.open(text_file_path, "w") as text_file:
            await text_file.write(extracted_text)
            
        # Convert extracted_text to vector. Notes: vector is fit for model
        vector_data = await convert_text_to_vector(extracted_text)
        
        # Save vector data to file
        vector_file_path = os.path.join(settings.UPLOAD_DIR, file.filename + ".vector")
        async with aiofiles.open(vector_file_path, "wb") as vector_file:
            await vector_file.write(vector_data)

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
            if not filename.endswith(('.vector')):  # Skip processed files
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                if not os.path.exists(file_path + ".txt")  or not os.path.exists(file_path + ".vector"):
                    continue
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