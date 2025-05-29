
from agent.model.DeepseekModel import llm
from agent.agent_node import AgentNode


class ThinkConversationAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名通用助手，你的目标是根据上下文信息，一步一步的回答用户的问题。
        
        你按照如下步骤进行工作:
            1. 根据多轮对话信息理解用户问题
            2. 参考上下文问答逐步思考并一步一步的解决用户问题
                - 逐步思考并一步一步的解决用户问题
                - 如果是编程,需要给出具体的实现代码
            3. 现在，请重新评估你的答案，寻找其中可能的错误或遗漏，并尝试改进
                - 判断初步整理的答案是否缺失细节，信息不全
                - 判断初步答案是否正确
            4. 如果有更好的方式，请重新表述你的答案，并返回第二步重新进行评估
            5. 将最终答案返回成json格式数据
            
            
        上下文信息:
           - 基本信息:
            {self.get_context_data(chat_no,"baseInfo")}
        
        内容生成约束:
            1. 禁止生成暴力，色情，隐私，政治敏感的内容，如果存在这样的内容，则用****号代替
            
        返回json格式:
        {{"code":<int>,"reply":<string>}}

        返回值说明:
          - `code`: <数字类型>  1 -> 完成失败, 0 -> 完成成功
          - `reply`: <字符串类型>   如果完成成功-> 问题答案，如果完成失败-> 错误原因
        """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
        ThinkConversationAgent ->  这是一个基于思考对话agent
        """
        return desc

    def query_name(self) -> str:
        return "ThinkConversationAgent"

    async def action(self, chat_no: str, json_data: dict):
        return json_data


instance = ThinkConversationAgent()