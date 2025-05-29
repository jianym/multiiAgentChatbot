from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from model.AgentTask import AgentTask

class AgentTaskDao:


    # async def insert(self, session: AsyncSession,sql: str):
    #     session.execute(sql)
    #     await session.flush()  # 确保插入数据库并更新 session 状态（但不提交）
    #     await session.refresh(agentTask)  # 刷新对象状态，获取最新数据
    #     return agentTask


    async def query(self, session: AsyncSession,pageSize: int):
        # 原生 SQL 查询
        sql = f"SELECT id,task_name,task_cron,task_content,create_time FROM agent_task LIMIT :pageSize"

        # 执行查询
        result = await session.execute(text(sql),{"pageSize":pageSize})
        result = result.fetchall()  # 获取所有结果
        agentTasks = [{"id": row[0], "taskName": row[1], "taskCron": row[2],"taskContent": row[3],"createTime": row[4]} for row in result]
        return agentTasks

    async def createTask(self, session: AsyncSession, agentTask: AgentTask):
        session.add(agentTask)
        await session.flush()  # 确保插入数据库并更新 session 状态（但不提交）
        await session.refresh(agentTask)  # 刷新对象状态，获取最新数据
        return agentTask

agentTaskDao = AgentTaskDao()