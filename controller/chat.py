from fastapi import APIRouter, Request
from agent.AgentQueryGraphBuild import queryGraph

router = APIRouter(
    prefix="/chat"
)

@router.get("/completions")
async def completions(chatNo: str,content: str, request: Request):
    response = await queryGraph.start(chatNo,content)
    return response


