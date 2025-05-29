import asyncio
import json
import time

from common.RedisManager import r
from agent.model.BgeModel import bgeModel
from dao.MemoryMilvusDao import instance
from agent.model.DeepseekModel import llm
class AgentMemory:

    memory_prefix = "agent_memory_"

    def add_message(self,chat_no: str,content: dict):
        r.rpush(AgentMemory.memory_prefix+chat_no, json.dumps(content, ensure_ascii=False))
        # self.storeMessage([content])

    def get_message(self, chat_no: str):
        messages = r.lrange(AgentMemory.memory_prefix+chat_no, 0, -1)
        message_dict = []
        for msg in messages:
            json_data = json.loads(msg.decode('utf-8'))
            message_dict.append({"role": json_data["role"],"content":json_data["content"]})
        asyncio.create_task(self.summary_messsage(message_dict,chat_no))
        return message_dict

    async def summary_messsage(self,message_dict: list,chat_no: str):
        if len(message_dict) > 50:
            list_length = r.llen(AgentMemory.memory_prefix + chat_no)
            conversation_message_list = message_dict[0:24]
            content = f"""
            你的工作职责是对多轮对话信息进行总结压缩，输出总结压缩后的内容
            
            多轮对话信息:
            {conversation_message_list}
            """
            summary_result = await llm.acall(json.dumps({"role":"user","content": content}),response_format="text")
            r.ltrim(AgentMemory.memory_prefix + chat_no, list_length - 25, list_length - 1)
            r.lpush(AgentMemory.memory_prefix+chat_no, json.dumps({"role": "assistant","content": summary_result}, ensure_ascii=False))

    def split_text_sliding_window(self, text, window_size=512, stride=128):
        """滑动窗口分割文本"""
        chunks = [text[i:i + window_size] for i in range(0, len(text), stride)]
        return chunks


memory = AgentMemory()