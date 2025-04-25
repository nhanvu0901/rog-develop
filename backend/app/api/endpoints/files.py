import os
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

# Định nghĩa thư mục lưu trữ file
UPLOAD_DIR = "uploads"  # Đảm bảo thư mục này tồn tại

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"File {filename} not found"
            )
        
        # Xóa file
        os.remove(file_path)
        os.remove(file_path + ".txt")
        os.remove(file_path + ".vector")
        
        return {"message": f"File {filename} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        ) 