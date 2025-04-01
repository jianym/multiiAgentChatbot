import os

from fastapi import APIRouter,UploadFile, File
from service.knowkledgeService import knowledageServiceInstance
import config

import shutil
router = APIRouter(
    prefix="/knowledge"
)

# 确保 uploads 目录存在
UPLOAD_DIR = "knowledge"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/")
async def upload_file(chatNo: str, file: UploadFile = File(...)):
    file_location = f"{config.OS_BASE_PATH}/{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    knowledageServiceInstance.store(file,chatNo)

    return {"filename": file.filename, "saved_path": file_location}
