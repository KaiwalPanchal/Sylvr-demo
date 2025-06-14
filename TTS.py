from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
from gtts import gTTS
import uuid
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loading Whisper model once during startup
model = whisper.load_model("small")

# directory to store files
if not os.path.exists("tmp"):
    os.makedirs("tmp")

@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribes an uploaded audio file to text."""
    file_location = f"tmp/{uuid.uuid4()}.wav"

    with open(file_location, "wb") as f:
        f.write(await file.read())

    result = model.transcribe(file_location)
    text = result["text"]

    os.remove(file_location)

    return {"transcribed_text": text}

@app.post("/tts")
async def text_to_speech(text: str = Form(...)):
    """Converts text to speech using Google TTS."""
    file_location = f"tmp/{uuid.uuid4()}.mp3"
    
    tts = gTTS(text=text, lang='en')
    tts.save(file_location)
    
    response = FileResponse(
        file_location,
        media_type="audio/mpeg",
        filename="speech.mp3"
    )
    
    # Clean up the file after sending
    response.background = lambda: os.remove(file_location)
    
    return response
