from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.services.transcription import transcribe_audio
from backend.app.services.minutes import generate_minutes

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
    # save uploaded file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename}

@app.post("/v1/transcribe/{filename}")
async def transcribe(filename: str):
    transcript = await transcribe_audio(f"temp/{filename}")
    return {"transcript": transcript}

@app.post("/v1/generate_minutes/")
async def generate(transcript: str):
    minutes = await generate_minutes(transcript)
    return {"minutes": minutes}