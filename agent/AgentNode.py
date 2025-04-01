import json
import time

from agent.AgentTool import Tool


class Node(Tool):

    knowledgeDict = {}

    def __init__(self):
        super().__init__()
        self.childs = []

    def addChild(self, node):
        self.childs.append(node)






