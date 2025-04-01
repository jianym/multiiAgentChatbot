from agent.AgentTool import Tool
from agent.tool.AgentImport import agentImport

class AgentToolImport:


    def __init__(self):
        self.toolDict = {}
        scheduleTool = agentImport.loadAgent("modules/ScheduleTool.py", "ScheduleTool")
        emailModule = agentImport.loadAgent("modules/EmailTool.py", "EmailTool")
        commonTool = agentImport.loadAgent("modules/CommonTool.py", "CommonTool")
        searchTool = agentImport.loadAgent("modules/SearchTool.py", "SearchTool")
        fileSystemTool = agentImport.loadAgent("modules/FileSystemTool.py", "FileSystemTool")
        omniCommonTool = agentImport.loadAgent("modules/OmniCommonTool.py", "OmniCommonTool")
        self.setTool("EmailTool", emailModule.instance)
        self.setTool("ScheduleTool", scheduleTool.instance)
        self.setTool("CommonTool", commonTool.instance)
        self.setTool("SearchTool", searchTool.instance)
        self.setTool("FileSystemTool", fileSystemTool.instance)
        self.setTool("OmniCommonTool", omniCommonTool.instance)

    def queryAgents(self) -> str:
        content = ""
        for key in self.toolDict:
            content += self.toolDict[key].queryDesc()
        return content

    def getTool(self,name: str) -> str:
        return self.toolDict[name]

    def setTool(self,name: str, tool: Tool):
        self.toolDict[name] = tool


tools = AgentToolImport()