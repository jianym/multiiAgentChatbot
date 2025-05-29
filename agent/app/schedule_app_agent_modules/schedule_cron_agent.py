from datetime import datetime
from agent.agent_node import AgentNode
from agent.model.DeepseekModel import llm
import json

from common.TransactionManager import Propagation, transactional
from sqlalchemy.ext.asyncio import AsyncSession
from dao.AgentSqlDao import agent_sql_dao


class ScheduleCronAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.tool_data = ""
        self.llm = llm

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名cron定时任务计划管理助手，可以使用已有工具解决问题。
        
        你将按照如下流程工作
            1. 根据多轮对话理解用户意图，提取定时任务执行时间和执行内容
            2. 编写定时任务表sql语句，调用相关工具传入相关参数对定时任务表进行操作
        
        基本信息:
        {self.get_context_data(chat_no, "baseInfo")}
        
        定时任务cron格式:
            5位数格式: 分 时 日 月 星期
                分 -> 0–59 -> 每小时的第几分钟
                时 -> 0–23 -> 每天的第几个小时
                日 -> 1–31 -> 每月的第几天
                月 -> 1–12 -> 每年的第几月
                星期 -> 	0–7（0 和 7 都表示星期日）-> 每周的星期几
            例子:
            0 5 * * *
            30 14 * * 1
            0 0 1 1 *
            */10 * * * * 

          
        上下文信息:
        
            定时任务表:
            CREATE TABLE `agent_task` (
                `id` varchar(64) NOT NULL DEFAULT '' COMMENT '主键',
                `task_name` varchar(64) DEFAULT '' COMMENT '任务名称',
                `task_content` varchar(512) DEFAULT '' COMMENT '任务内容',
                `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                `task_cron` varchar(64) DEFAULT '' COMMENT '触发时间',
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


        返回json格式:
        {{"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name": <string>,"args": <list>}}

        返回值说明:
          - `code`：0 -> 执行成功 1 -> 缺少任务cron执行时间，缺少任务的执行内容，sql语句不是对定时任务表进行增删改查操作
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `reply`:  
                - code为0: sql语句信息
                - code为1: 识别原因
          - `tool_name`: 调用工具的名称
          - `args`: 调用工具所需的参数列表

        可调用工具信息:
          - `insert(sqls: list)`: 向定时任务表中插入数据(可以同时插入多条定时任务的sql语句)
            - `sqls`: 必需传递，插入的sql语句集合
          - `query(sql: str)`: 通过sql语句查询定时任务
            - `sql`: 必需传递，查询的sql语句
        """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
              ScheduleCronAgent -> 这是一个任务计划管理Agent，工作职责是处理周期类等非立即执行的问题。可以使用已有工具解决问题:
              """
        return desc

    def query_name(self) -> str:
        return "ScheduleCronAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] != 0:
            return json_data
        if json_data["tool_name"] == "insert":
            self.tool_data = await self.insert(sql=json_data["args"][0])
        if json_data["tool_name"] == "query":
            self.tool_data = await self.query_by_sql(sql=json_data["args"][0])
            
        return {"code": 0, "reply": json.dumps(self.tool_data, default=self.serialize_datetime)}

    @transactional(propagation=Propagation.REQUIRES_NEW)
    async def insert(self, session: AsyncSession, sqls: list):
        for sql in sqls:
            await agent_sql_dao.insert(session=session, sql=text(sql))
        return "成功"

    @transactional(propagation=Propagation.REQUIRES_NEW)
    async def query_by_sql(self, session: AsyncSession, sql: str):
        result = await agent_sql_dao.query_by_sql(session=session, sql=text(sql))
        return result

    def serialize_datetime(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()  # 'YYYY-MM-DDTHH:MM:SS.ssssss'
        raise TypeError(f"Type {type(obj)} not serializable")


instance = ScheduleCronAgent()