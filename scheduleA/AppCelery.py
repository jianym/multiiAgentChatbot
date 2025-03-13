from celery import Celery
from celery.schedules import crontab
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from agent.AgentTaskGraphBuild import taskGraph
from common.TransactionManager import transactional, Propagation
from dao.AgentTaskDao import agentTaskDao


# 初始化 Celery 应用
celeryApp = Celery('apps', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/1')

celeryApp.conf.update(
    timezone='Asia/Shanghai',
    enable_utc=False,
    result_backend=None,  # 不使用结果后端
)



@celeryApp.task
def taskGraphJob(taskId: str, taskContent: str):
    print("Task is running...")
    asyncio.run(taskGraph.start(taskId, taskContent))

class AppCelery:
    def __init__(self):
        # 通过事件循环运行查询操作
        asyncio.get_event_loop().run_until_complete(self.query())

    @transactional(propagation=Propagation.REQUIRES_NEW)
    async def query(self, session: AsyncSession):
        agentTasks = await agentTaskDao.query(session, 1000)
        for item in agentTasks:
            self.addDynamicTask(item["taskCron"], item["id"], item["taskContent"])

    def parseCron(self, cron: str):
        minute, hour, day_of_week, day_of_month, month_of_year = cron.split()
        return crontab(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year)

    def addDynamicTask(self, cron: str, taskId: str, taskContent: str):
        # 使用 crontab 表达式添加任务
        celeryApp.add_periodic_task(
            self.parseCron(cron),  # 定时任务的 Cron 表达式
            taskGraphJob.s(taskId=taskId, taskContent=taskContent),  # 任务函数和其参数
            name=f"task-{taskId}"  # 为任务命名，确保唯一
        )
        print(cron)
        print(taskContent)

    def removeDynamicTask(self, taskId):
        taskName = f"task-{taskId}"
        if taskName in celeryApp.conf.beat_schedule:
            del celeryApp.conf.beat_schedule[taskName]  # 从计划任务中删除
            celeryApp.conf.beat_schedule = celeryApp.conf.beat_schedule  # 刷新调度器
            print(f"Task {taskName} removed successfully.")
        else:
            print(f"Task {taskName} not found.")

appCelery = AppCelery()