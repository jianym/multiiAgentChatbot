
import ast
import json

from agent.agent_node import AgentNode
from agent.info_context import InfoContext
from agent.model.DeepseekModel import llm
from agent.agent_import import agent_import


class PlanningRouteAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def get_prompt(self, chat_no=None):
        content = f"""
            你是一名预处理规划智能体，按照流程进行工作

            如果用户没有明确要求，你必须按照如下流程步骤顺序执行,不可跳过中间步骤，从infer阶段开始执行:
            
               首先执行infer阶段进行预处理推理，然后执行task进行任务分配，最后执行final给出最终答案
               
               1.infer: 首先，结合多轮对话信息与上下文信息来理解用户问题（包括用户的实际问题，话题是否切换，判断回答问题的语言），返回相关信息
                  - 话题切换检测: 判断用户是否跳出原始任务，及时引导或重启会话
                  - 用户的实际问题: 补全上下文信息和文字内容纠错后的用户实际问题
                  - 判断回答问题的语言: 默认与用户问题的语言一致（语言: 中文，english等），除非用户有明确的语言要求
               2.task: 然后，将用户问题按照功能拆分成独立任务并进行Agent分配
               3.final: 最后，保持各任务的执行结果内容不变，返回整体的答案
               
            用户问题拆分独立任务例子:
               1.如果用户问题包含多个互不影响的独立任务则进行拆分
               2.如果用户问题包含多个有相互关系的任务，一个Agent可以解决则分配给一个Agent，否则分配给多个Agent
               
               例如:
                 用户问题: 生成一篇散文文章，给我一张去北京的火车票信息，下载生成的散文
                 任务拆分及分配: [{{"task":" 生成一篇散文文章并提供下载链接","agent_name":"WritingRouteAgent"}},{{"task":"搜索一张去北京的火车票","agent_name":"ConversationRouteAgent"}}]
                 
            
            上下文信息:
                - 基本信息:
                    {self.get_context_data(chat_no, "baseInfo")}
            
            以下情况分配失败:
                - 用户问题意义不明，表达混乱
                - 没有能够解决用户问题的Agent

            已知Agent信息:
               [
                 {{ 
                    "name": "ConversationAppAgent",
                    "desc": "处理信息检索类，回答类，数学类，数学制图类，方程表达式等NLP相关问题"
                 }},{{
                    "name": "CrossModalAppAgent",
                    "desc": "多模态类非数学类问题处理"
                 }},{{
                    "name": "WritingAppAgent",
                    "desc": "NLP写作类（公文，散文）问题处理，包括写作，润色，部分修改，内容格式化，下载（提供word，pdf，txt）等相关功能"
                 }},{{
                    "name": "ScheduleAppAgent",
                    "desc": "进行cron定时类任务，延时类等非立即执行类任务，"
                 }},{{
                    "name": "RpaAppAgent",
                    "desc": "进行邮件发送等操作"
                 }}
               ]
               
            返回值json格式如下: 
            {{"code": 0,step:<string>,"reply":<object>}}

            返回值说明:
            - `code`: 0 -> 完成分类 1 -> 失败原因
            - `step`: 当前执行步骤， infer/task/final
            - `reply`: 
                如果step为infer，reply -> {{"is_topic":<bool>,"query":<string>,"language": <string>}}
                    - `is_topic`: 是否切换主题
                    - `query`: 用户的实际问题
                    - `language`: 回复用户问题应该使用的语言,如：英语，中文，日语，德语...等
                如果step为task，reply -> [{{"task":<string>,"agent_name":<string>}}]
                    - `task`: 需要执行的任务
                    - `agent_name`: 执行任务的agent名称
                如果step为final，reply -> string，最终答案

        """
        message = {"role": "system", "content": content}
        return message

    def query_name(self) -> str:
        return "PlanningRouteAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] == 1:
            return json_data
        if json_data["step"] == "infer":
            reply = ast.literal_eval(json_data["reply"])
            language = reply["language"]
            InfoContext.baseInfoDict[chat_no].update({
                "默认语言": f"""你必须强制使用{language}语言来输出问题答案（包括解释和说明部分），即使内容中包含英文术语或代码"""})
            self.append_message(chat_no,
                                         {"role": "user", "content": f"""infer阶段执行完成，执行task阶段进行任务分配与处理"""})
            return await self.exec(chat_no)
        if json_data["step"] == "task":
            tasks = ast.literal_eval(json_data["reply"])

            for task in tasks:
                agent_instance = agent_import.get_agent(task["agent_name"])

                agent_instance.append_message(chat_no,

                                             {"role": "user", "content": json.dumps(self.message_dict[chat_no][0:-1])})
                agent_instance.append_message(chat_no,
                                             {"role": "user", "content": f"""当前任务: {task["task"]}"""})
                result = await agent_instance.exec(chat_no)
                self.append_message(chat_no,{"role":"assistant","content":f"""任务: {task["task"]} 的执行结果为:{result} """ })
            self.append_message(chat_no,{"role": "user", "content": f"""任务分配及执行阶段已完成,执行final阶段给出最终答案。"""})
            return await self.exec(chat_no)
        return json_data

