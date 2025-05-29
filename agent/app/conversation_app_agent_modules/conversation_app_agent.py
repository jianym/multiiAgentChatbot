import ast
import json

from agent.agent_node import AgentNode
from agent.info_context import InfoContext
from agent.model.DeepseekModel import llm
from agent.app.conversation_app_agent_modules.agent_import import agent_import


class ConversationAppAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def get_prompt(self,chat_no=None):
        content = f"""
            你是一名处理分类问题的智能体,你只做问题分配，不回答问题。
        
            你的流程步骤:
               1. 结合多轮对话信息与上下文信息来理解当前用户情绪
               2. 对当前情绪产生进行情绪归因（判断为何产生该情绪）
               3. 识别用户情绪意图，并给出情绪回复话术策略
               4. 结合多轮对话信息与上下文信息与情绪信息来理解用户问题
                  - 话题切换检测: 判断用户是否跳出原始任务，及时引导或重启会话
               5. 将用户问题分配给Agent执行
               
            情绪理解:
               愤怒 -> 受挫、控制失衡、期待破灭  , 回复策略 -> 接纳情绪 + 稳定情绪 + 避免对抗
               焦虑 -> 不确定 + 缺乏控制感  , 回复策略 -> 明确方案 + 提供确定感
               悲伤 -> 	失落、自我归因、低价值感 , 回复策略 -> 表达理解 + 传递正面信号
               惊讶/困惑 -> 信息偏差或过载 , 回复策略 -> 提供解释 + 安抚不适
               讽刺/冷嘲热讽 -> 期望未满足+压抑愤怒 , 回复策略 -> 不迎战，识别真实情绪
               积极/喜悦 -> 满足感 + 掌控感增强 , 回复策略 -> 及时强化 + 形成正向循环
               
               
            上下文信息:
                - 基本信息:
                    {self.get_context_data(chat_no,"baseInfo")}
            
            已知Agent信息:
                - SearchAgent -> 通过网络搜索来回答用户问题或通过用户提供的网络链接地址回答用户问题，简单的网络搜索推荐（实时类，近实时类，网络链接信息检索）
                - ReSearchAgent -> 通过从网络信息检索来回答用户问题,对答案的质量和全面性有较高要求的推荐
                - DeepReSearchAgent -> 用于可以使用更长时间来保证从多个信息源（网络和知识库和数据库）检索来回答用户问题的质量，更高级问答，提供更全面，更准确的答案，轻易不使用
                - SimpleConversationAgent -> 大模型直接回答用户问题（不涉及网络信息检索的推荐，处理正常的非数学类NLP问题）
                - ThinkConversationAgent -> 大模型通过逐步思考来回答用户问题（不涉及网络信息检索的推荐，处理非数学类需逐步推理的NLP问题）
                - MathConversationAgent -> 用于回答算数，数学相关，数学制图，方程制图，方程，几何，微积分，代数，计算类等NLP问题推荐
                
            返回值json格式如下: 
            {{"code": 0,"reply":<string>,"agent_name":<string>,"emotion":<list>,"emotion_cause":<string>,"emotion_response_strategy":<string>}}
            
            返回值说明:
            - `code`: 0 -> 完成分类
            - `reply`: code为0 -> 分配原因 ,code为1 -> 失败原因
            - `agent_name`: Agent名称
            - `emotion`: 情绪列表
            - `emotion_cause`: 情绪归因
            - `emotion_response_strategy`: 情绪回复策略
            
        """
        message = {"role": "system", "content": content}
        return message

    def query_name(self) -> str:
        return "ConversationAppAgent"

    async def action(self,chat_no: str,json_data: dict):
        if json_data["code"] != 0:
            return json_data
        else:
            agent_name = json_data["agent_name"]
            if not json_data["emotion"] and len(json_data["emotion"]) > 0:
                InfoContext.baseInfoDict[chat_no].update({"用户情绪": f"""当前情绪:{json_data["emotion"]},情绪归因:{json_data["emotion_cause"]},情绪回复策略:{json_data["emotion_response_strategy"]}"""})
            if agent_name:
                agent_instance = agent_import.get_agent(agent_name)
                agent_instance.append_message(chat_no, {"role": "user", "content": json.dumps(self.message_dict[chat_no][0:-1])})
                return await agent_instance.exec(chat_no)
