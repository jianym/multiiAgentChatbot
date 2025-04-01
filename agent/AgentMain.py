
from agent.AgentNode import Node
from agent.model.DeepseekModel import llm

class AgentMain(Node):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def getPrompt(self,messageNo=None):
        content = """
            你是一名处理分类问题的智能体,你只是分类，不回答问题。
            你的工作职责是结合多轮对话信息与基本信息来理解用户问题，然后将用户问题分配给Agent执行。
              
            基本信息:
            {self.baseInfo}
            
            返回值json格式如下: 
            {"code": 0,"reply":"...","agentName":"..."}
            
            返回值说明:
            - `code`: 0 -> 完成分类
            - `reply`: code为0 -> 分类原因
            - `agentName`: Agent名称
            
            已知Agent信息:
            - simpleAgent -> 常识类，知识类，文字类，问答类，内容类，内容生成类问题
            - agentPlanning -> 近实时信息，最近时间信息，网络搜索，联网解决，操作系统类，多模态，涉及action等与程序外部交互或需要调用工具解决的问题

        """
        message = {"role": "system", "content": content}
        return message

    def queryName(self) -> str:
        return "mainAgent"

    async def action(self,messageNo: str,jsonData: dict):
        messages = self.getMessageAndPrompt(messageNo)
        if jsonData["code"] != 0:
            return jsonData
        else:
            print(jsonData)
            agentName = jsonData["agentName"]
            if agentName == "simpleAgent":
                self.childs[0].appendMessages(messageNo, messages[1:-1])
                jsonData = await self.childs[0].exec(messageNo)
                return jsonData
            elif agentName == "agentPlanning":
                self.childs[1].appendMessages(messageNo, messages[1:-1])
                jsonData = await self.childs[1].exec(messageNo)
                self.appendMessage(messageNo, {"role": "assistant", "content":  jsonData["reply"]})
                return jsonData
            elif agentName == "novelAgent":
                self.childs[2].appendMessages(messageNo, messages[1:-1])
                jsonData = await self.childs[2].exec(messageNo)
                self.appendMessage(messageNo, {"role": "assistant", "content":  jsonData["reply"]})
                return jsonData
