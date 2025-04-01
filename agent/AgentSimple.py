
from agent.AgentNode import Node
from agent.model.DeepseekModel import llm

class AgentSimple(Node):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.tryTime = 2

    def getPrompt(self, messageNo=None):
        content = f"""
        你是一名通用问答助手，你的目标是根据多轮对话信息理解用户意图从而回答用户的问题。
        
        基本信息:
        {self.baseInfo}
        
        你按照如下步骤进行工作:
            1. 根据多轮对话信息理解用户问题
            2. 问答用户问题，如果知识库存在已知信息，需要参考知识库相关信息做出回答
            3. 现在，请重新评估你的答案，寻找其中可能的错误或遗漏，并尝试改进
                - 判断初步整理的答案是否缺失细节，信息不全
                - 判断初步答案是否正确
            3. 如果有更好的方式，请重新表述你的答案，并返回第三步重新进行评估
            4. 将最终答案返回成json格式数据
        
        作为参考的知识库信息:
        {Node.knowledgeDict.get(messageNo)}
        
        返回json格式:
        {{"code":0,"reply":<string>}}
        
        返回值说明:
          - `code`: 0 -> 完成成功
          - `reply`: <字符串类型>   如果完成成功-> 问题答案，如果完成失败-> 错误原因
        
        """
        message = {"role": "system", "content": content}
        return message

    def queryDesc(self) -> str:
        desc = """
        simpleAgent -> 如果其他Agent不满足，使用这个，这是一个通用的Agent
        """
        return desc

    def queryName(self) -> str:
        return "simpleAgent"

    async def action(self,messageNo: str,jsonData: dict):
        return jsonData