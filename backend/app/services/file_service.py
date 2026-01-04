from app.models.chat import FileUpload, FileType, FileReference
from typing import Optional
import uuid


class FileService:
    def __init__(self):
        # In-memory storage (simulated file uploads)
        self.files: dict[str, FileUpload] = {}
    
    def upload_file(self, filename: str, size: int, content_type: str) -> FileUpload:
        """Simulate file upload (fictitious)"""
        file_id = str(uuid.uuid4())
        
        # Determine file type based on content type or extension
        file_type = self._determine_file_type(filename, content_type)
        
        # Simulate file path
        file_path = f"/uploads/{file_id}/{filename}"
        
        file_upload = FileUpload(
            id=file_id,
            path=file_path,
            type=file_type,
            filename=filename,
            size=size
        )
        
        self.files[file_id] = file_upload
        return file_upload
    
    def get_file(self, file_id: str) -> Optional[FileUpload]:
        """Get file information by ID"""
        return self.files.get(file_id)
    
    def get_file_reference(self, file_id: str) -> Optional[FileReference]:
        """Get file reference for storage in conversation"""
        file = self.files.get(file_id)
        if not file:
            return None
        
        return FileReference(
            id=file.id,
            path=file.path,
            type=file.type,
            filename=file.filename
        )
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID"""
        if file_id in self.files:
            del self.files[file_id]
            return True
        return False
    
    def _determine_file_type(self, filename: str, content_type: str) -> FileType:
        """Determine file type from filename or content type"""
        filename_lower = filename.lower()
        
        # Check image types
        if content_type.startswith('image/') or filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
            return FileType.IMAGE
        
        # Check PDF
        if 'pdf' in content_type or filename_lower.endswith('.pdf'):
            return FileType.PDF
        
        # Check Word documents
        if 'word' in content_type or filename_lower.endswith(('.doc', '.docx')):
            return FileType.WORD
        
        return FileType.OTHER


# Singleton instance
file_service = FileService()
