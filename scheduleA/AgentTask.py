# import asyncio
#
# from schedule.AppCelery import app
# from celery.schedules import crontab
# from agent.AgentTaskGraphBuild import taskGraph
#
# # 定义一个简单的任务函数
# @app.task
# def taskGraph(taskId: str,taskContent: str):
#     print("5555555555555")
#     print("5555555555555")
#     print("5555555555555")
#     print("5555555555555")
#     asyncio.run(taskGraph.start(taskId,taskContent))
#
#
# def parseCron(cron: str):
#     minute,hour,day_of_week,day_of_month,month_of_year = cron.split()
#     return crontab(minute=minute,hour=hour,day_of_week=day_of_week,day_of_month=day_of_month,month_of_year=month_of_year)
#
# # 动态添加任务的函数
# def addDynamicTask(cron: str, taskId: str,taskContent: str):
#     # 使用 crontab 表达式添加任务
#     app.add_periodic_task(
#         parseCron(cron),  # 定时任务的 Cron 表达式
#         taskGraph.s(taskId, taskContent),  # 任务函数和其参数
#         name=f"task-{taskId}"  # 为任务命名，确保唯一
#     )
#     print("6666666666")
#
# # 移除任务的函数
# def removeDynamicTask(taskId):
#     taskName = f"task-{taskId}"
#     if taskName in app.conf.beat_schedule:
#         del app.conf.beat_schedule[taskName]  # 从计划任务中删除
#         app.conf.beat_schedule = app.conf.beat_schedule  # 刷新调度器
#         print(f"Task {taskName} removed successfully.")
#     else:
#         print(f"Task {taskName} not found.")