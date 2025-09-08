""""""

import os
from typing import Dict, Any, Optional
from fastapi import UploadFile
import PyPDF2
import docx
import markdown
from datetime import datetime
import os
from typing import List

try:
    import pytesseract  # OCR
except Exception:
    pytesseract = None  # type: ignore

try:
    from pdf2image import convert_from_path  # PDF -> images
except Exception:
    convert_from_path = None  # type: ignore


class FileService:
    
    SUPPORTED_TYPES = {
        'text/plain': '.txt',
        'text/markdown': '.md',
        'application/pdf': '.pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/msword': '.doc'
    }
    
    def __init__(self, upload_dir: str = "./data"):
        self.upload_dir = upload_dir
        self._ensure_upload_dir()
        # Configure OCR tool paths if available
        try:
            if pytesseract is not None:
                pytesseract.pytesseract.tesseract_cmd = os.getenv(
                    "TESSERACT_CMD", "/opt/homebrew/bin/tesseract"
                )
        except Exception:
            pass
    
    def _ensure_upload_dir(self):
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def is_supported_file(self, file: UploadFile) -> bool:
        return file.content_type in self.SUPPORTED_TYPES
    
    def get_file_extension(self, file: UploadFile) -> str:
        return self.SUPPORTED_TYPES.get(file.content_type, '')
    
    async def save_file(self, file: UploadFile) -> Dict[str, Any]:
        try:
            if not self.is_supported_file(file):
                return {
                    "success": False,
                    "message": f"Unsupported file type: {file.content_type}",
                    "error": "Unsupported file type"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = self.get_file_extension(file)
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(self.upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return {
                "success": True,
                "message": "Saved",
                "file_path": file_path,
                "filename": filename,
                "file_size": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Save failed: {str(e)}",
                "error": str(e)
            }
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        try:
            if file_type == 'text/plain':
                return self._extract_from_txt(file_path)
            elif file_type == 'text/markdown':
                return self._extract_from_markdown(file_path)
            elif file_type == 'application/pdf':
                return self._extract_from_pdf(file_path)
            elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                return self._extract_from_docx(file_path)
            else:
                return {
                    "success": False,
                    "content": "",
                    "message": f"Unsupported file type: {file_type}",
                    "error": "Unsupported file type"
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"Extract failed: {str(e)}",
                "error": str(e)
            }
    
    def _extract_from_txt(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return {
                "success": True,
                "content": content,
                "message": "TXT parsed"
            }
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    content = file.read()
                return {
                    "success": True,
                    "content": content,
                    "message": "TXT parsed (GBK)"
                }
            except Exception as e:
                return {
                    "success": False,
                    "content": "",
                    "message": f"TXT parse failed: {str(e)}",
                    "error": str(e)
                }
    
    def _extract_from_markdown(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
            
            html = markdown.markdown(md_content)
            import re
            content = re.sub('<[^<]+?>', '', html)
            
            return {
                "success": True,
                "content": content,
                "message": "Markdown parsed"
            }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"Markdown parse failed: {str(e)}",
                "error": str(e)
            }
    
    def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"
            
            if not content.strip():
                ocr_result = self._ocr_pdf(file_path)
                if ocr_result["success"] and ocr_result["content"].strip():
                    return ocr_result
                return ocr_result
            
            return {
                "success": True,
                "content": content,
                "message": f"PDF parsed, pages: {len(pdf_reader.pages)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"PDF parse failed: {str(e)}",
                "error": str(e)
            }

    def _ocr_pdf(self, file_path: str) -> Dict[str, Any]:
        if pytesseract is None or convert_from_path is None:
            return {
                "success": False,
                "content": "",
                "message": "OCR not available. Install tesseract and pdf2image.",
                "error": "OCR dependencies missing"
            }
        try:
            poppler_path = os.getenv("POPPLER_PATH", "/opt/homebrew/bin")
            images: List["Image.Image"] = convert_from_path(
                file_path, dpi=300, poppler_path=poppler_path
            )
            text_chunks: List[str] = []
            for img in images:
                text = pytesseract.image_to_string(img)
                if text:
                    text_chunks.append(text)
            content = "\n".join(text_chunks)
            if not content.strip():
                return {
                    "success": False,
                    "content": "",
                    "message": "OCR found no text",
                    "error": "No text content found"
                }
            return {"success": True, "content": content, "message": "OCR parsed PDF"}
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"OCR failed: {str(e)}",
                "error": str(e)
            }
    
    def _extract_from_docx(self, file_path: str) -> Dict[str, Any]:
        try:
            doc = docx.Document(file_path)
            content = ""
            
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            
            if not content.strip():
                return {
                    "success": False,
                    "content": "",
                    "message": "No text content in DOCX",
                    "error": "No text content found"
                }
            
            return {
                "success": True,
                "content": content,
                "message": "DOCX parsed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"DOCX parse failed: {str(e)}",
                "error": str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": "File not found",
                    "error": "File not found"
                }
            
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "filename": os.path.basename(file_path),
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Get file info failed: {str(e)}",
                "error": str(e)
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "success": True,
                    "message": "Deleted"
                }
            else:
                return {
                    "success": False,
                    "message": "File not found",
                    "error": "File not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Delete failed: {str(e)}",
                "error": str(e)
            }
