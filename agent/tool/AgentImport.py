import os
import importlib.util


class AgentImport:

     base_dir = os.path.dirname(os.path.abspath(__file__))

     def loadAgent(self, relativePath: str, name: str):
          file_path = os.path.join(self.base_dir, relativePath)
          spec = importlib.util.spec_from_file_location(name, file_path)
          module = importlib.util.module_from_spec(spec)
          spec.loader.exec_module(module)
          return module

agentImport = AgentImport()
