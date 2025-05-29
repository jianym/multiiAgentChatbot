import uuid

from fastapi import APIRouter, Request, UploadFile, File
from perception.speechRecognition import audio_thread

router = APIRouter(
    prefix="/speech"
)

@router.get("/mc/start")
async def mcStart():
    if not audio_thread.is_alive():
        audio_thread.setChatNo(uuid.uuid4())
        audio_thread.start()

@router.get("/mc/stop")
async def mcStop():
    audio_thread.stop()






