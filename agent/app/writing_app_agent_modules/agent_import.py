import os
import importlib.util

class AgentImport:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_dict = {}

        office_gen_agent = self.load_agent("office_gen_agent.py", "OfficeGenAgent")
        prose_gen_agent = self.load_agent("prose_gen_agent.py", "ProseGenAgent")

        self.set_agent("OfficeGenAgent", office_gen_agent)
        self.set_agent("ProseGenAgent", prose_gen_agent)


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