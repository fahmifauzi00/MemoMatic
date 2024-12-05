from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app import transcribe_audio, generate_minutes, create_docx, rate_limiter, file_cache
from typing import Optional
import os
from urllib.parse import unquote
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# create a temp directory if it doesn't exist
os.makedirs(TEMP_DIR, exist_ok=True)


title = "MemoMatic API"
description = "MemoMatic API"
__version__ = "0.1"

app = FastAPI(
    title=title,
    description=description,
    version=__version__
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root(request: Request = None):
    client_host = request.client.host
    return {
        'message': 'Memomatic API',
        'version': __version__,
        'client_host': client_host
    }
    
@app.get("/v1/rate-limit-status", tags=["Rate Limit"])
async def get_rate_limit_status(request: Request):
    """Get current rate limit status"""
    client_ip = request.client.host
    return rate_limiter.check_status(client_ip)

@app.post("/v1/start-cycle", tags=["Rate Limit"])
async def start_cycle(request: Request):
    """Start a new transcription cycle"""
    client_ip = request.client.host
    is_allowed, rate_info = rate_limiter.start_cycle(client_ip)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "rate_limit_info": rate_info
            }
        )
    return rate_info
    
@app.post("/v1/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    """Handle file upload with caching"""
    logger.info(f"Received file upload request: {file.filename}")
    
    # Check if file already exists in cache
    if file_cache.file_exists(file.filename):
        logger.info(f"File {file.filename} already exists in cache")
        return {"filename": file.filename}
    
    try:
        file_path = os.path.join(TEMP_DIR, file.filename)
        logger.info(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            logger.info(f"File saved successfully, size: {len(content)} bytes")
            
        # Add file to cache
        file_cache.add_file(file.filename, file_path)
        return {"filename": file.filename}
        
    except Exception as e:
        error_msg = f"Error uploading file: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/v1/transcribe/{filename}")
async def transcribe(
    filename: str,
    request: Request,
    session_id: str
):
    """Transcribe audio using cached file"""
    try:
        # Validate session
        rate_info = rate_limiter.check_status(request.client.host)
        if not rate_info["active_cycle"] or rate_info["session_id"] != session_id:
            raise HTTPException(
                status_code=400,
                detail="No active transcription cycle. Please start a new cycle."
            )
            
        # Get file from cache
        decoded_filename = unquote(filename)
        file_path = file_cache.get_file_path(decoded_filename)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {decoded_filename}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
            
        transcript = await transcribe_audio(file_path)
        logger.info("Transcription completed successfully")
        
        return {
            "transcript": transcript,
            "rate_limit_info": rate_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error during transcription: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


class MinutesRequest(BaseModel):
    transcript: str
    session_id: Optional[str] = None
    
@app.post("/v1/generate_minutes")
async def generate(request: MinutesRequest, req: Request):
    logger.info("Starting minutes generation")
    try:
        if request.session_id:
            rate_info = rate_limiter.check_status(req.client.host)
            
            if not rate_info["active_cycle"] or rate_info["session_id"] != request.session_id:
                raise HTTPException(
                    status_code=400,
                    detail="No active transcription cycle. Please start a new cycle."
                )
            
        # generate minutes content
        minutes_content = await generate_minutes(request.transcript)
        
        #parse the minutes content from string to dictionary
        try:
            # first try to parse it as JSON
            minutes_dict = json.loads(minutes_content)
        except json.JSONDecodeError:
            # if it's not JSON, create a simple format
            minutes_dict = {
                "title": "Meeting Minutes",
                "summary": minutes_content,
                "key_points": [],
                "action_items": [],
                "decisions": []
            }
            
        # create docx file
        docx_path = create_docx(minutes_dict)
        logger.info(f"DOCX file created at: {docx_path}")
        
        return {"minutes": minutes_content}
        
    except Exception as e:
        error_msg = f"Error generating minutes: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)