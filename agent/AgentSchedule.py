from datetime import datetime

from agent.AgentGraph import Node
from agent.model.BaseModel import BaseModel
import json
from dao.AgentTaskDao import agentTaskDao
from model.AgentTask import AgentTask
from common.TransactionManager import Propagation, transactional
from sqlalchemy.ext.asyncio import AsyncSession

class AgentSchedule(Node):

    def getPrompt(self):
        content = {"role": "system", "content":
            f"你是一名邮件发送助手，可以使用已有工具解决问题: \n"
            "你的工作职责是分别提取触发时间和触发内容和任务名称并调用工具创建，更新，删除cron任务。\n"
            " 触发时间：任务开始执行时间，提取出的时间需要转换成cron格式 \n"
            " 触发内容：触发时需要执行的具体内容 \n"
            " 任务名称：当前任务的名称，任务的标识 \n"
            "返回json格式:\n"
            "{\"status\":2,\"reply\":\"...\",\"tool_use\": true, \"tool_name\":tool_name,\"args\": [...]}} \n"
            "返回值说明： \n"
            " status: 0 -> 提取触发时间或触发事件有误需用户处理, 2 -> 执行成功 \n"
            " reply: status为2 -> 问题解决信息, status为0 -> 需要补充的信息 \n"
            " tool_use: true -> 需使用工具, false -> 不使用工具 \n"
            " tool_name: 工具名称 \n"
            " args: 参数列表 \n"
            "已有工具信息: \n"
            "  - insert(event: list): 插入数据，参数event结构为[{cron: str,content: str,name: str}], cron -> 触发时间cron, content -> 触发内容（不包含触发时间） \n"
            "  - query(): 查询数据 \n"
            }
        return content



    def queryDesc(self) -> str:
        return "这是一个用来处理定时任务的工具"

    def create(self,cron: str,content: str):
        pass

    def update(self,cron: str,content: str,id: str):
        pass

    def delete(self,id: str):
        pass


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



    async def exec(self, messageNo: str,llm: BaseModel) -> str:
        response = await llm.acall(json.dumps(self.messageDict[messageNo]))

        jsonData = json.loads(response)
        self.reply = jsonData["reply"]
        if jsonData["status"] == 2:
                if jsonData["tool_name"] == "insert":
                     await self.insert(events=jsonData["args"][0])
                elif jsonData["tool_name"] == "query":
                     responseInstance = await self.query()
                     jsonData["data"] = json.dumps(responseInstance, default=self.datetimeConverter, ensure_ascii=False)
                     self.reply =self.reply + " " + jsonData["data"]
                     jsonData["reply"] = self.reply

        self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
        return json.dumps(jsonData)

    def datetimeConverter(self,obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')  # 将 datetime 格式化为字符串
        raise TypeError("Type not serializable")