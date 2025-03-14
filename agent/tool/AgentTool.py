# This is a sample Python script.
from agent.AgentGraph import Node
from agent.tool.AgentImport import agentImport
from agent.AgentSimple import AgentSimple
class AgentTool:


    def __init__(self):
        self.toolDict = {}
        # searchTool = agentImport.loadAgent("modules/SearchTool.py", "SearchTool")
        ScheduleTool = agentImport.loadAgent("modules/ScheduleTool.py", "ScheduleTool")
        emailModule = agentImport.loadAgent("modules/EmailTool.py", "EmailTool")
        # self.setTool("SearchTool", searchModule.instance)
        self.setTool("EmailTool", emailModule.instance)
        self.setTool("ScheduleTool", ScheduleTool.instance)
        self.setTool("simpleAgent", AgentSimple())



    def queryAgents(self) -> str:
        content = ""
        for key in self.toolDict:
            content += self.toolDict[key].queryDesc()
        return content

    def getTool(self,name: str) -> str:
        return self.toolDict[name]

    def setTool(self,name: str, tool: Node):
        self.toolDict[name] = tool


tools = AgentTool()