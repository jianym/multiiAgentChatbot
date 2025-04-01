
import json
import aiohttp
from agent.model.BaseModel import BaseModel
import ssl
import config

# 创建一个 SSLContext 来禁用证书验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class QwenModel(BaseModel):

    api_url: str = config.QWEN_URL

    api_key: str = config.QWEN_API_Key

    def call(self):
        print("调用成功")

    async def acall(self, messages: str) -> str:
        """这个方法会用来调用自定义 API，并返回结果"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        print(json.loads(messages))
        payload = {
            "model": "qwen-omni-turbo",
            "messages": json.loads(messages),
            "stream": True,
            "stream_options": {"include_usage": True},
            # "response_format": {
            #     "type": "json_object"
            # },
            "modalities": ["text"]

            # "temperature": temperature,
            # "top_p": top_k,
            # "frequency_penalty": frequencyPenalty
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=ssl_context)) as session:
            async with session.post(f"{self.api_url}/chat/completions", json=payload, headers=headers) as response:
                response.raise_for_status()  # 抛出HTTP异常
                self.responseData = ""
                # 逐块处理流式数据
                async for chunk in response.content.iter_any():
                    if chunk:
                        try:
                            # 解码每个数据块
                            chunk_str = chunk.decode('utf-8').strip()
                            if not chunk_str:
                                continue  # 如果是空的块，跳过

                            # 打印调试信息，查看块内容
                            # print(f"收到的块内容: {chunk_str}")

                            # 解析每个 JSON 事件（假设每个事件以换行符分隔）
                            events = chunk_str.split("\n")  # 如果有多个事件数据块，可以按行分割
                            for event in events:
                                if event:

                                    try:

                                        if event.startswith("data:"):
                                            event = event[5:].strip()
                                        if event == "[DONE]":
                                            return self.responseData
                                        # 将每个事件块解析为 JSON
                                        completion = json.loads(event)
                                        if 'choices' in completion:
                                            if len(completion['choices']) > 0:
                                                content = completion['choices'][0]["delta"].get("content", '')
                                                if content != None:
                                                    self.responseData = self.responseData+content
                                        else:
                                            print("Usage:", completion.get('usage', '没有 usage 数据'))
                                    except json.JSONDecodeError as e:
                                        raise e
                                        print(f"解码事件块时出错: {e}")
                        except Exception as e:
                            raise e
                            print(f"处理数据块时出错: {e}")
                    else:
                        print("接收到的数据块为空。")

                return self.responseData
llmQwen = QwenModel()
