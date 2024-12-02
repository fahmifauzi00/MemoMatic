from openai import OpenAI
from config import settings

async def transcribe_audio(file_path: str):
    client = OpenAI(
        base_url=settings.MESOLITICA_API_URL,
        api_key=settings.MESOLITICA_API_KEY,
    )
    
    try:
        with open(file_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model="base",
                file=audio_file,
                language=["en", "ms"]
            )
        return result.text
    except Exception as e:
        raise Exception(f"Transcription error: {str(e)}")