import os
import importlib.util

class AgentImport:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_dict = {}

        email_agent = self.load_agent("email_agent.py", "EmailAgent")
        self.set_agent("EmailAgent", email_agent)

    def query_agents(self) -> str:
        return ''.join(agent.queryDesc() for agent in self.agent_dict.values())

    def get_agent(self, name: str):
        return self.agent_dict[name]

    def set_agent(self, name: str, tool):
        self.agent_dict[name] = tool

    def load_agent(self, relative_path: str, class_mame: str):
        file_path = os.path.join(self.base_dir, relative_path)
        spec = importlib.util.spec_from_file_location(class_mame, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        cls = getattr(module, class_mame)
        return cls()  # 实例化类
agent_import = AgentImport()