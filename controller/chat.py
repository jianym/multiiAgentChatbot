import json
import os
import shutil
import uuid

from fastapi.responses import JSONResponse

import config
from fastapi import APIRouter, Request, UploadFile, File
from agent.query_route_agent import queryRoute
from agent.agent_memory import memory
router = APIRouter(
    prefix="/chat"
)


@router.get("/completions")
async def completions(chatNo: str,content: str, knowledge=False):
    return await queryRoute.start(chatNo,content)



@router.get("/conv")
async def conv(chat_no: str):
    convs = []
    messageDict = memory.getMessage(chat_no)
    if len(messageDict) > 0:
        for item in messageDict:
            convs.append({"reply": item["content"]})
    return convs


@router.get("/generate/id")
async def generateId():
    return uuid.uuid4()

@router.get("/generate/title")
async def generateTitle(chat_no: str):
    return "测试"

@router.post("/upload/")
async def upload_file(chat_no: str, file: UploadFile = File(...)):
    file_location = f"{config.OS_BASE_PATH}/{chat_no}/tmp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"code": 0, "saved_path": file.filename}

@router.get("/download")
async def download(chat_no: str, basePath: str):
    filePath = config.OS_BASE_PATH + "/" + chat_no + "/" + basePath
    if os.path.exists(filePath):
        return JSONResponse(
            content={"code": 0, "basePath": basePath},
            headers={"X-File-Download": filePath}
        )
    else:
        return {"code": 10001, "msg": "File generation failed"}





