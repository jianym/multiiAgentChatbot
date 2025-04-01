import json
import time

from common.RedisManager import r

class AgentMemory:

    memory_prefix = "agent_memory_"

    def addMessage(self,messageNo: str,content: dict):
        r.rpush(AgentMemory.memory_prefix+messageNo, json.dumps(content, ensure_ascii=False))

    def getMessage(self, messageNo: str):
        messages = r.lrange(AgentMemory.memory_prefix+messageNo, 0, -1)
        messageDict = []
        for msg in messages:
            jsonData = json.loads(msg.decode('utf-8'))
            messageDict.append({"role": jsonData["role"],"content":jsonData["content"]})
        if len(messageDict) > 50:
            self.summaryMessage(messageDict[-25:-1])
            list_length = r.llen(AgentMemory.memory_prefix+messageNo)
            r.ltrim(AgentMemory.memory_prefix+messageNo, list_length-25, list_length-1)
        return messageDict

    def summaryMessage(self,messageDict: list):
        return None

memory = AgentMemory()