from agent.info_context import InfoContext
from agent.planning_route_agent import PlanningRouteAgent
from common.memory_context_manager import MemoryContextManager


class QueryRouteAgent:

    def __init__(self):
        self.planning_route_agent = PlanningRouteAgent()

    async def start(self, chat_no: str, query: str):

        with MemoryContextManager(chat_no, query) as mc:
            json_data = await self.find_agent(chat_no,mc.memory_message)
            mc.set_reply(json_data["reply"])
            InfoContext.downFile.pop(chat_no, None)

        return json_data

    async def find_agent(self, chat_no: str,memory_message) -> dict:
        self.planning_route_agent.append_messages(chat_no, memory_message)
        json_data = await self.planning_route_agent.exec(chat_no)
        return json_data

queryRoute = QueryRouteAgent()
