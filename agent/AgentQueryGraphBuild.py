from agent.AgentMain import AgentMain
from agent.AgentNode import Node
from agent.AgentTool import Tool
from agent.AgentSimple import AgentSimple
from agent.AgentPlanning import AgentPlanning
from agent.exports.AgentNovel import AgentNovel
from agent.exports.AgentNovelChapter import AgentNovelChapter
from agent.exports.AgentNovelChapterDetail import AgentNovelChapterDetail
from agent.AgentMemory import memory
from service.knowkledgeService import knowledageServiceInstance

class AgentQueryGraphBuild:

    def __init__(self):
        self.chapterAgent = AgentNovelChapter()
        self.agentNovelChapterDetail = AgentNovelChapterDetail()
        self.agentMain = AgentMain()
        self.simpleAgent = AgentSimple()
        self.novelAgent = AgentNovel()
        self.agentPlanning = AgentPlanning()
        self.chapterAgent.addChild(self.agentNovelChapterDetail)
        self.novelAgent.addChild(self.chapterAgent)
        self.agentMain.addChild(self.simpleAgent)
        self.agentMain.addChild(self.agentPlanning)
        self.agentMain.addChild(self.novelAgent)

    def getUserPrompt(self,prompt: str):
         return {"role": "user", "content": prompt}

    async def start(self,messageNo: str, query: str,knowledge: bool):
        if knowledge:
             knowledgeData = knowledageServiceInstance.searchRAG(query,messageNo)
             Node.knowledgeDict[messageNo] = knowledgeData
        if query:
            memory.addMessage(messageNo, self.getUserPrompt(query))

        self.agentMain.appendMessages(messageNo,memory.getMessage(messageNo))
        jsonData = await self.agentMain.exec(messageNo)
        Node.knowledgeDict.pop(messageNo, None)

        memory.addMessage(messageNo, {"role": "assistant","content": jsonData["reply"]})
        filePath = Tool.downFile.pop(messageNo, None)
        jsonData["downFilePath"] = filePath

        return jsonData

queryGraph = AgentQueryGraphBuild()

