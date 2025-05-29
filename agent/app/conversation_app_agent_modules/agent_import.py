import os
import importlib.util

class AgentImport:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_dict = {}

        deep_re_search_agent = self.load_agent("deep_re_search_agent.py", "DeepReSearchAgent")
        math_conversation_agent = self.load_agent("math_conversation_agent.py", "MathConversationAgent")
        re_search_agent = self.load_agent("re_search_agent.py", "ReSearchAgent")
        search_agent = self.load_agent("search_agent.py", "SearchAgent")
        simple_conversation_agent = self.load_agent("simple_conversation_agent.py", "SimpleConversationAgent")
        think_conversation_agent = self.load_agent("think_conversation_agent.py", "ThinkConversationAgent")

        self.set_agent("DeepReSearchAgent", deep_re_search_agent)
        self.set_agent("MathConversationAgent", math_conversation_agent)
        self.set_agent("ReSearchAgent", re_search_agent)
        self.set_agent("SearchAgent", search_agent)
        self.set_agent("SimpleConversationAgent", simple_conversation_agent)
        self.set_agent("ThinkConversationAgent", think_conversation_agent)

    def query_agents(self) -> str:
        return ''.join(agent.queryDesc() for agent in self.agent_dict.values())

    def get_agent(self, name: str):
        return self.agent_dict[name]

    def set_agent(self, name: str, tool):
        self.agent_dict[name] = tool

    def load_agent(self, relative_path: str, class_name: str):
        file_path = os.path.join(self.base_dir, relative_path)
        spec = importlib.util.spec_from_file_location(class_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        cls = getattr(module, class_name)
        return cls()  # 实例化类
agent_import = AgentImport()