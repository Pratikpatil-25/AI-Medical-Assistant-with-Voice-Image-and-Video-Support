import os
import shutil
import base64
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from brain import doctor
from speech2text import transcribe_patient_voice
from text2speech import save_text2speech_file

app = FastAPI(title="AI Medical Assistant API")

# Allow the Streamlit frontend (different origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_upload(upload: UploadFile, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with tmp as f:
        shutil.copyfileobj(upload.file, f)
    return tmp.name


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Medical Assistant backend is running."}


@app.post("/ask")
async def ask(
    audio: UploadFile = File(...),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
):
    audio_path = image_path = video_path = tts_path = None
    try:
        audio_suffix = Path(audio.filename or "audio.wav").suffix or ".wav"
        audio_path = _save_upload(audio, audio_suffix)

        if image is not None and image.filename:
            image_suffix = Path(image.filename).suffix or ".jpeg"
            image_path = _save_upload(image, image_suffix)

        if video is not None and video.filename:
            video_suffix = Path(video.filename).suffix or ".mp4"
            video_path = _save_upload(video, video_suffix)

        try:
            transcription = transcribe_patient_voice(audio_filepath=audio_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

        try:
            doctor_response = doctor(
                patient_query=transcription,
                image_filepath=image_path,
                video_filepath=video_path,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Doctor model failed: {e}")

        tts_fd, tts_path = tempfile.mkstemp(suffix=".mp3")
        os.close(tts_fd)
        try:
            save_text2speech_file(text=doctor_response, save_filepath=Path(tts_path))
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {e}")

        with open(tts_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        return JSONResponse(
            {
                "transcription": transcription,
                "doctor_response": doctor_response,
                "audio_base64": audio_b64,
            }
        )
    finally:
        for p in (audio_path, image_path, video_path, tts_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))