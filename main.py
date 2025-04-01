from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request

from controller import chat
from controller import knowledge

app = FastAPI()
app.include_router(chat.router)
app.include_router(knowledge.router)


# 自定义全局异常处理器
@app.exception_handler(Exception)
async def globalExceptionHandler(request: Request, exc: Exception):
    # 打印异常详情或记录日志
    print(f"Unexpected error: {exc}")
    # 返回自定义错误信息
    return {"status": 500, "reply":""}


# 中间件：模拟 AOP，统一拦截所有请求
class SessionValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 在请求到达路由之前进行会话校验
        # check_session(request)

        # 执行请求处理
        response = await call_next(request)

        # 在响应返回之前，你可以在这里做一些后置操作（例如日志记录）
        return response

# 将中间件添加到应用中
app.add_middleware(SessionValidationMiddleware)


