import os
import shutil
import uuid

import config
from fastapi import APIRouter, Request, UploadFile, File
from agent.AgentQueryGraphBuild import queryGraph
from agent.AgentMemory import memory

router = APIRouter(
    prefix="/chat"
)

@router.get("/completions")
async def completions(chatNo: str,content: str, knowledge=False):
    return await queryGraph.start(chatNo,content,knowledge)

@router.get("/conv")
async def conv(chatNo: str):
    convs = []
    messageDict = memory.getMessage(chatNo)
    if len(messageDict) > 0:
        for item in messageDict:
            convs.append({"reply": item["content"]})
    return convs


@router.get("/generate/id")
async def generateId():
    return uuid.uuid4()

@router.get("/generate/title")
async def generateTitle(chatNo: str):
    return "测试"

@router.post("/upload/")
async def upload_file(chatNo: str, file: UploadFile = File(...)):
    file_location = f"{config.OS_BASE_PATH}/{chatNo}/tmp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"code": 0, "saved_path": file.filename}

@router.get("/download")
async def completions(chatNo: str, basePath: str):
    filePath = config.OS_BASE_PATH + "/" + chatNo + "/" + basePath
    if os.path.exists(filePath):
        return JSONResponse(
            content={"code": 0, "basePath": basePath},
            headers={"X-File-Download": filePath}
        )
    else:
        return {"code": 10001, "msg": "File generation failed"}





