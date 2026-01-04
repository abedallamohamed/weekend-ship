from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.chat import FileUpload
from app.services.file_service import file_service

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload", response_model=FileUpload)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (simulated - no actual file storage)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read file size (but don't store the actual content)
    content = await file.read()
    file_size = len(content)
    
    # Simulate file upload
    uploaded_file = file_service.upload_file(
        filename=file.filename,
        size=file_size,
        content_type=file.content_type or "application/octet-stream"
    )
    
    return uploaded_file


@router.get("/{file_id}", response_model=FileUpload)
async def get_file(file_id: str):
    """Get file information by ID"""
    file = file_service.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    success = file_service.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}
