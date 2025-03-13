import asyncio

from fastapi import FastAPI
from controller import chat


app = FastAPI()
app.include_router(chat.router)

