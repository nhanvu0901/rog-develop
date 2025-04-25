from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.app.core.config import settings

# Import and include routers
from backend.app.api.endpoints import file_processing, auth, chat, files

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(file_processing.router, prefix=settings.API_V1_STR, tags=["file-processing"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(files.router, prefix=settings.API_V1_STR, tags=["files"])

# Mount thư mục build của React
if (os.path.isdir(settings.WEB_FOLDER)):
    app.mount("/static", StaticFiles(directory=settings.WEB_FOLDER + "/static"), name="static")

# Route mặc định trả về index.html
@app.get("/")
async def read_index():
    if (os.path.isdir(settings.WEB_FOLDER) and os.path.isfile(settings.WEB_FOLDER + "/index.html")):
        return FileResponse(settings.WEB_FOLDER + "/index.html")
    return {"message": settings.PROJECT_NAME}

# Route bắt tất cả các path khác để hỗ trợ client-side routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    if (os.path.isfile(settings.WEB_FOLDER + "/" + full_path)):
        return FileResponse(settings.WEB_FOLDER + "/" + full_path)
    return FileResponse(settings.WEB_FOLDER + "/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)