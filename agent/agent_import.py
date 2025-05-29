import os
import importlib.util

class AgentImport:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_dict = {}

        conversation_app_agent = self.load_agent("app/conversation_app_agent_modules/conversation_app_agent.py", "ConversationAppAgent")
        writing_app_agent = self.load_agent("app/writing_app_agent_modules/writing_app_agent.py", "WritingAppAgent")
        cross_modal_app_agent = self.load_agent("app/cross_modal_app_agent_modules/cross_modal_app_agent.py", "CrossModalAppAgent")
        schedule_app_agent = self.load_agent("app/schedule_app_agent_modules/schedule_app_agent.py", "ScheduleAppAgent")
        rpa_app_agent = self.load_agent("app/rpa_app_agent_modules/rpa_app_agent.py", "RpaAppAgent")

        self.set_agent("ConversationAppAgent", conversation_app_agent)
        self.set_agent("WritingAppAgent", writing_app_agent)
        self.set_agent("CrossModalAppAgent", cross_modal_app_agent)
        self.set_agent("ScheduleAppAgent", schedule_app_agent)
        self.set_agent("RpaAppAgent", rpa_app_agent)


    def query_agents(self) -> str:
        return ''.join(tool.queryDesc() for tool in self.agent_dict.values())

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