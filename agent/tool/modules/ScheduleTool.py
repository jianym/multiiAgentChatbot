from datetime import datetime

from agent.AgentTool import Tool
from agent.model.DeepseekModel import llm
import json

from dao.AgentTaskDao import agentTaskDao
from model.AgentTask import AgentTask
from common.TransactionManager import Propagation, transactional
from sqlalchemy.ext.asyncio import AsyncSession

class ScheduleTool(Tool):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def getPrompt(self, messageNo=None):
        content = """
        你是一名任务计划管理助手，可以使用已有工具解决问题。
        你的工作职责是分别提取和分割触发时间和触发内容和任务名称并调用工具对任务计划进行管理
          - 触发时间：任务开始执行时间
          - 触发内容：触发时需要执行的具体内容
          - 任务名称：当前任务的名称，任务的标识
        
        返回json格式:
        {"code":<int>,"reply":<string>,"tool_use": <bool>, "tool_name":<string>,"args":<list>}} 
       
        返回值说明:
          - `code`：1 -> 触发时间和触发内容缺失, 0 -> 执行成功
          - `reply`: `code` 为 0 -> 提供问题解决信息， `code` 为 1 -> 需要补充的信息 
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `tool_name`: 使用的工具名称
          - `args`: 工具所需的参数列表
          
        已有工具信息:
          - `insert(event: list)`: 插入周期cron格式任务计划
            - `event`: 描述 -> 参数event结构为[{cron: <string>,content: <string>,name: <string>}]
                -  `cron` -> 描述 -> 触发时间cron;  验证 -> 不能为空，5位标准
                -  `content` -> 描述 -> 到达触发时间时需要执行的内容（不包含触发时间）; 验证 -> 不能为空
          - `query()`: 查询已有任务计划
        """
        message = {"role": "system", "content": content}
        return message


    def queryDesc(self) -> str:
        desc = """
              ScheduleTool -> 这是一个任务计划管理Agent，工作职责是处理周期类，延时类等非立即执行的问题。可以使用已有工具解决问题:
                - `insert(event: list)`: 插入周期cron格式的任务计划
                    - `event`: 描述 -> 参数event结构为[{cron: <string>,content: <string>,name: <string>}]
                        - `cron` -> 描述 -> 触发时间cron;  验证 -> 不能为空，5位标准
                        - `content` -> 描述 -> 到达触发时间时需要执行的内容（不包含触发时间）; 验证 -> 不能为空
                - `query()`: 查询已有任务计划
              """
        return desc

    def queryName(self) -> str:
        return "ScheduleTool"

    @transactional(propagation=Propagation.REQUIRES_NEW)
    async def query(self,session: AsyncSession):
        return await agentTaskDao.query(session,10)

    @transactional(propagation=Propagation.REQUIRES_NEW)
    async def insert(self,session: AsyncSession,events: list):
        agentTasks = []
        for item in events:
            agentTask = AgentTask()
            agentTask.taskContent = item["content"]
            agentTask.taskCron = item["cron"]
            agentTask.taskName = item["name"]
            await agentTaskDao.createTask(session,agentTask)
            agentTasks.append(agentTask)
        return agentTasks



    async def action(self,messageNo: str,jsonData: dict):

        if jsonData["code"] == 0:
                if jsonData["tool_name"] == "insert":
                     await self.insert(events=jsonData["args"][0])
                elif jsonData["tool_name"] == "query":
                     responseInstance = await self.query()
                     jsonData["data"] = json.dumps(responseInstance, default=self.datetimeConverter, ensure_ascii=False)
                     self.reply =self.reply + " " + jsonData["data"]
                     jsonData["reply"] = self.reply
        return jsonData

    def datetimeConverter(self,obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')  # 将 datetime 格式化为字符串
        raise TypeError("Type not serializable")

instance = ScheduleTool()