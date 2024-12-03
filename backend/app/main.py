from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app import transcribe_audio, generate_minutes, create_docx
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
    
@app.post("/v1/upload_audio/")
async def upload_audio(file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")
    try:
        file_path = os.path.join(TEMP_DIR, file.filename)
        logger.info(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            logger.info(f"File saved successfully, size: {len(content)} bytes")
            
        return {"filename": file.filename}
    except Exception as e:
        error_msg = f"Error uploading file: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/v1/transcribe/{filename}")
async def transcribe(filename: str):
    try:
        # Decode the URL-encoded filename
        decoded_filename = unquote(filename)
        file_path = os.path.join(TEMP_DIR, decoded_filename)
        logger.info(f"Starting transcription for file: {decoded_filename}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            error_msg = f"File not found: {decoded_filename}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            error_msg = "File is empty"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        transcript = await transcribe_audio(file_path)
        logger.info("Transcription completed successfully")
        return {"transcript": transcript}
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error during transcription: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


class MinutesRequest(BaseModel):
    transcript: str
    
@app.post("/v1/generate_minutes")
async def generate(request: MinutesRequest):
    logger.info("Starting minutes generation")
    try:
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