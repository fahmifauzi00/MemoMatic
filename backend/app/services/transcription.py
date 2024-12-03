# backend/app/services/transcription.py
import logging
from openai import OpenAI
from config import settings
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

async def transcribe_audio(file_path: str):
    """
    Transcribe audio file using Mesolitica API.
    """
    logger.info(f"Starting transcription for file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        error_msg = f"File not found at path: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    # Check file size
    file_size = os.path.getsize(file_path)
    logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
    
    try:
        client = OpenAI(
            base_url=settings.MESOLITICA_API_URL,
            api_key=settings.MESOLITICA_API_KEY,
        )
        
        logger.info("Initialized OpenAI client")
        
        with open(file_path, "rb") as audio_file:
            logger.info("Sending transcription request...")
            transcript = client.audio.transcriptions.create(
                model="base",
                file=audio_file,
                response_format="text",
            )
            logger.info("Transcription completed successfully")
            return transcript
            
    except Exception as e:
        error_msg = f"Transcription error: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)