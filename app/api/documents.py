""""""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from ..models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentInfo,
    StatsResponse,
)
from ..services.rag_service_groq import RAGServiceGroq
from ..services.file_service import FileService

router = APIRouter(prefix="/documents", tags=["Documents"])

rag_service = RAGServiceGroq()
file_service = FileService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        if not file_service.is_supported_file(file):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        save_result = await file_service.save_file(file)
        if not save_result["success"]:
            raise HTTPException(status_code=500, detail=save_result["message"])
        
        extract_result = file_service.extract_text_from_file(
            save_result["file_path"], 
            file.content_type
        )
        
        if not extract_result["success"]:
            file_service.delete_file(save_result["file_path"])
            raise HTTPException(status_code=500, detail=extract_result["message"])
        
        document_id = str(uuid.uuid4())
        
        metadata = {
            "document_id": document_id,
            "filename": file.filename,
            "type": file.content_type,
            "file_size": save_result["file_size"],
            "upload_time": datetime.now().isoformat(),
            "file_path": save_result["file_path"]
        }
        
        add_result = rag_service.add_document(
            content=extract_result["content"],
            metadata=metadata
        )
        
        if not add_result["success"]:
            file_service.delete_file(save_result["file_path"])
            raise HTTPException(status_code=500, detail=add_result["message"])
        
        return DocumentUploadResponse(
            success=True,
            message="Document uploaded",
            document_id=document_id,
            filename=file.filename,
            file_size=save_result["file_size"],
            chunks_count=add_result["chunks_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    try:
        stats = rag_service.get_document_stats()
        
        documents = []
        if stats["total_documents"] > 0:
            documents.append(DocumentInfo(
                document_id="sample_id",
                filename="Sample",
                file_type="text/plain",
                file_size=1024,
                upload_time=datetime.now().isoformat(),
                chunks_count=stats["total_documents"]
            ))
        
        return DocumentListResponse(
            success=True,
            documents=documents,
            total_count=stats["total_documents"]
        )
        
    except Exception as e:
        return DocumentListResponse(success=False, error=f"List failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_document_stats():
    try:
        stats = rag_service.get_document_stats()
        
        return StatsResponse(
            success=True,
            total_documents=stats["total_documents"],
            document_types=stats["document_types"],
            vector_db_size=stats["vector_db_size"],
            last_updated=stats["last_updated"]
        )
        
    except Exception as e:
        return StatsResponse(success=False, error=f"Stats failed: {str(e)}")


@router.delete("/clear")
async def clear_all_documents():
    try:
        result = rag_service.clear_all_documents()
        
        if result["success"]:
            return {"success": True, "message": "All documents cleared"}
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")


@router.get("/search")
async def search_documents(query: str, limit: int = 5):
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query must not be empty")
        
        results = rag_service.search_similar(query, k=limit)
        
        return {
            "success": True,
            "results": results,
            "query": query,
            "total_results": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
