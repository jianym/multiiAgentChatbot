
import json
import aiohttp
import ssl
import config
from framework.base_model import BaseModel

# 创建一个 SSLContext 来禁用证书验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class DeepseekModel(BaseModel):

    api_url: str = config.DEEPSEEK_URL

    api_key: str = config.DEEPSEEK_API_Key

    def call(self, messages: str, **kwargs) -> str:
        pass

    async def acall(self, messages: str,**kwargs) -> str:
        """这个方法会用来调用自定义 API，并返回结果"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": json.loads(messages),
            "stream": False,
            **kwargs
        }
        timeout = aiohttp.ClientTimeout(total=120)
        # 使用自定义 SSL 配置
        async with aiohttp.ClientSession(timeout=timeout,connector=aiohttp.TCPConnector(ssl_context=ssl_context)) as session:
            # 在任务中调用 API
            async with session.post(f"{self.api_url}/chat/completions", json=payload, headers=headers) as response:
                response.raise_for_status()  # 抛出HTTP异常
                response_data = await response.json()  # 异步获取 JSON 数据
                return response_data["choices"][0]["message"]["content"]


llm = DeepseekModel()
