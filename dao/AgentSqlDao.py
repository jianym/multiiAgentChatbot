import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class AgentSqlDao:


    async def query(self, session: AsyncSession,sql):
        # 执行查询
        result = await session.execute(sql,{"db_name": "agent_link"})
        result = result.fetchall()  # 获取所有结果
        return result

    async def insert(self, session: AsyncSession, sql):
        await session.execute(sql, {})

    async def query_by_sql(self, session: AsyncSession, sql):
        result = await session.execute(sql, {})
        result = result.mappings().all()
        return [dict(row) for row in result]



agent_sql_dao = AgentSqlDao()