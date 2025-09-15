from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
import aiofiles
import os
import uuid
from typing import List
import logging
import PyPDF2
import io
from docx import Document
import tempfile

from database import get_database
from models.user import User
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Configure upload settings
UPLOAD_DIR = os.getenv("UPLOAD_PATH", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/file", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload and process a single file"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF, DOCX, DOC, and TXT files are allowed."
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // 1024 // 1024}MB."
            )
        
        # Extract text based on file type
        extracted_text = ""
        
        try:
            if file_ext == ".pdf":
                extracted_text = await extract_pdf_text(file_content)
            elif file_ext in [".docx", ".doc"]:
                extracted_text = await extract_docx_text(file_content)
            elif file_ext == ".txt":
                extracted_text = file_content.decode("utf-8")
            
        except Exception as extraction_error:
            logger.error(f"File extraction error: {extraction_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract text from file"
            )
        
        # Validate extracted text
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract sufficient text from the file"
            )
        
        # Calculate word and character counts
        word_count = len(extracted_text.split())
        char_count = len(extracted_text)
        
        return {
            "success": True,
            "message": "File processed successfully",
            "data": {
                "originalName": file.filename,
                "fileType": file_ext,
                "extractedText": extracted_text.strip(),
                "wordCount": word_count,
                "characterCount": char_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

@router.post("/files", response_model=dict)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload and process multiple files"""
    try:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many files. Maximum 5 files per upload."
            )
        
        processed_files = []
        
        for file in files:
            try:
                # Validate file
                if not file.filename:
                    continue
                
                # Check file extension
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in ALLOWED_EXTENSIONS:
                    continue
                
                # Check file size
                file_content = await file.read()
                if len(file_content) > MAX_FILE_SIZE:
                    continue
                
                # Extract text
                extracted_text = ""
                try:
                    if file_ext == ".pdf":
                        extracted_text = await extract_pdf_text(file_content)
                    elif file_ext in [".docx", ".doc"]:
                        extracted_text = await extract_docx_text(file_content)
                    elif file_ext == ".txt":
                        extracted_text = file_content.decode("utf-8")
                except Exception as extraction_error:
                    logger.error(f"Error processing file {file.filename}: {extraction_error}")
                    continue
                
                # Validate extracted text
                if extracted_text and len(extracted_text.strip()) >= 50:
                    processed_files.append({
                        "originalName": file.filename,
                        "fileType": file_ext,
                        "extractedText": extracted_text.strip(),
                        "wordCount": len(extracted_text.split()),
                        "characterCount": len(extracted_text)
                    })
                    
            except Exception as file_error:
                logger.error(f"Error processing file {file.filename}: {file_error}")
                continue
        
        if not processed_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid files could be processed"
            )
        
        # Calculate totals
        total_word_count = sum(file["wordCount"] for file in processed_files)
        total_char_count = sum(file["characterCount"] for file in processed_files)
        
        return {
            "success": True,
            "message": f"{len(processed_files)} files processed successfully",
            "data": {
                "files": processed_files,
                "totalWordCount": total_word_count,
                "totalCharacterCount": total_char_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multiple file upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

@router.get("/supported-types", response_model=dict)
async def get_supported_file_types():
    """Get supported file types and limits"""
    return {
        "success": True,
        "data": {
            "supportedTypes": [
                {
                    "type": "PDF",
                    "extension": ".pdf",
                    "mimeType": "application/pdf",
                    "maxSize": "10MB",
                    "description": "Portable Document Format files"
                },
                {
                    "type": "DOCX",
                    "extension": ".docx",
                    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "maxSize": "10MB",
                    "description": "Microsoft Word documents (2007+)"
                },
                {
                    "type": "DOC",
                    "extension": ".doc",
                    "mimeType": "application/msword",
                    "maxSize": "10MB",
                    "description": "Microsoft Word documents (legacy)"
                },
                {
                    "type": "TXT",
                    "extension": ".txt",
                    "mimeType": "text/plain",
                    "maxSize": "10MB",
                    "description": "Plain text files"
                }
            ],
            "maxFileSize": MAX_FILE_SIZE,
            "maxFilesPerUpload": 5
        }
    }

async def extract_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise

async def extract_docx_text(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            
            # Open with python-docx
            doc = Document(temp_file.name)
            
            # Extract text from all paragraphs
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise

