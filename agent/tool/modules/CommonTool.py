from agent.AgentTool import Tool
from agent.model.DeepseekModel import llm
from agent.AgentNode import Node


class CommonTool(Tool):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def getPrompt(self, messageNo=None):
        content = f"""
        你是一名通用助手，你的目标是根据上下文信息，回答用户的问题。
        
        你按照如下步骤进行工作:
            1. 根据多轮对话信息与基本信息理解用户问题
            2. 如果知识库存在已知信息，则参考知识库相关信息做出回答
                - 如果是编程,需要给出具体的实现代码
            3. 现在，请重新评估你的答案，寻找其中可能的错误或遗漏，并尝试改进
                - 判断初步整理的答案是否缺失细节，信息不全
                - 判断初步答案是否正确
            4. 如果有更好的方式，请重新表述你的答案，并返回第二步重新进行评估
            5. 将最终答案返回成json格式数据
        
        基本信息:
        {self.baseInfo}
         
        返回json格式:
        {{"code":<int>,"reply":<string>}}

        返回值说明:
          - `code`: <数字类型>  1 -> 完成失败, 0 -> 完成成功
          - `reply`: <字符串类型>   如果完成成功-> 问题答案，如果完成失败-> 错误原因
        
        知识库信息:
        {Node.knowledgeDict.get(messageNo)}
        """
        message = {"role": "system", "content": content}
        return message

    def queryDesc(self) -> str:
        desc = """
        CommonTool ->  这是一个通用的Agent，如果其他Agent不满足，可以使用这个，主要解决解决知识类，常识类，问答类，逻辑类，文字类，内容类，内容生成类等问题
        """
        return desc

    def queryName(self) -> str:
        return "CommonTool"

    async def action(self, messageNo: str, jsonData: dict):
        return jsonData

instance = CommonTool()