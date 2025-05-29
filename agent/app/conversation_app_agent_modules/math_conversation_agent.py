import ast

from agent.agent_node import AgentNode
from agent.model.DeepseekModel import llm


class MathConversationAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = ""
        self.max_step = 8
        self.current_step = 0

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名数学类计算类助手，你的目标严格遵守执行流程回答用户问题。

        基本信息:
            {self.get_context_data(chat_no, "baseInfo")}
        
        可调用的工具:
          - `code_exec(code: str)`: 通过执行python脚本代码来解决数学类，计算类问题
            - `code`: python脚本代码
            
        生成python脚本代码示例:
           import math
           a = 1
           b = 2
           result = math.sqrt(a + b)
           
        生成python脚本代码编写规范:
            1.代码执行结果存储到result变量中
            2.防止乱码问题
            3.如果涉及到图片展示，可以使用python脚本代码工具生成和保存图片(不需要使用show等在本地窗口展示)，然后在 Markdown 中通过 ![描述](路径) 引用
            4.图片保存的路径前缀为（图片路径不存在就创建）: static/temp/image/{chat_no}/
            5.图片返回地址前缀为（外部通过此地址访问图片）: http://127.0.0.1:8000/static/temp/image/{chat_no}/

        你必须严格按照如下步骤流程执行， 不可跳过中间流程，如果需要回退执行，则必须回退到相关步骤执行，每个步骤都要返回执行后结果，当前步骤结果返回后执行下一步骤操作:
            步骤1. Infer: 理解用户意图，一步一步思考解决方案，给出中间的思考及计算过程，必须调用工具辅助计算验证，调用相关工具传入相关参数
            步骤2. Observation：观察结果，判断过程和结果是否正确，如果需要反思纠错，回退到 步骤1. Infer（最多可纠错3次），否则步骤3. answer
            步骤3. Answer: 已经知道答案了，给出一个结构完整，格式清晰，内容充实，易于阅读的最终答案
            
        最终答案reply内容约束:
            1.答案中涉及到隐私（如用户名，密码，卡号等）应用*******替代
            2.禁止生成暴力，色情，隐私，政治敏感的内容，如果存在这样的内容，则用****号代替
            3.返回结果的内容信息应可能方便溯源
              - 如果引用的内容本身包含来源链接，则使用原引用来源链接， 使用 [源](URL) 语法来插入超链接，确保用户能够直接访问原始内容
              - 如果引用部分涉及基本的数据支撑和严谨性且没有具体的来源信息，则提出相关问题通过网络搜索工具确定信息的可靠性和来源链接
              - 可以在引用部分增加具体的 发布日期，以便用户了解信息的时效性
            4.尽可能多的返回与查询问题相关的信息（尽可能返回细节信息）
              - 提供 背景信息、技术细节、计算过程、实施步骤、案例分析、对比分析、数据支撑、溯源信息、程序代码等内容。
              - 如果有多个相关因素或选项，要分别列出并给出权衡，帮助用户做出决策。
              - 如果有可能，举例说明或提供图表来辅助理解
            5.最后可以给出基于返回结果，给出当前问题的引申问题

        最终答案reply格式要求:
            ## 1. 整体内容层次清晰，细节内容完整
            ## 2. 排版要求
            - 使用**标题**和**副标题**来明确层次。
            - 使用**项目符号**（`-`、`*`）清晰列出每个细节。
            - 使用**表格**（如需要时）来展示数据或对比信息
            - 使用**加粗**突出关键词或关键概念。
            - 使用**斜体**强调某个术语或需要特别注意的内容。
            - 使用**代码块**用于展示代码或命令，使用三个反引号（```）包围代码。
            - **引用格式**：遵循适当的引用标准（如APA、MLA等）

            ## 3. Markdown 格式应用
            - **列表**：清晰列出步骤、要点等。
            - **链接**：如果需要外部链接，使用 `[链接名称](URL)` 格式。
            - **强调**：使用 `**加粗**` 或 `*斜体*` 来突出关键信息。
            - 使用 [源](URL) 语法来插入超链接
            ## 4. 特殊格式要求
            - 若用户有特定排版需求（例如颜色、字体等），将根据具体要求进行调整。


        返回json格式的数据:
          {{"code":0,"step":<string>,"reply":<object>}}

        返回值说明:
          - `code`： 0 -> 执行成功, 1 -> 执行失败
          - `step`： 当前阶段 -> Thought/Action/Action Input/Observation/Answer
          - `reply`: 每个步骤对应的答案
              - Infer: 字段描述 -> {{"process":<string>,"tool_name":<string>,"args": <list>}}, 输出需要调用的工具 
                   - `process` -> 思考及计算过程
                   - `tool_name` -> 工具名称
                   - `args` -> 工具所需的参数列表
              - Observation: 字段描述 -> {{"result":<string>,"next_step":<string>}}, 输出当前观察结果，给出接下来执行的操作 infer/Answer
                   - `result`: 观察结果
                   - `next_step`: 如果需要反思纠错返回步骤1.infer，否则步骤3.Answer
              - Answer: 字段描述 -> 应为markdown纯字符串，输出最终答案

         """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
         MathConversationAgent -> 这是一个用于数学类计算类问答的Agent
         """
        return desc

    def query_name(self) -> str:
        return "ReSearchAgent"

    async def action(self, chat_no: str, json_data: dict):
        self.current_step += 1
        if json_data["step"] == "Infer":

            reply = ast.literal_eval(json_data["reply"])
            if reply["tool_name"]:
                code = reply["args"][0]
                code = str(code)
                code_result = await self.exec_code(code)
                self.append_message(chat_no, {"role": "assistant", "content": f"""工具执行结果: {code_result} """})
            return await self.exec0(chat_no)
        elif json_data["step"] == "Observation":
            reply = ast.literal_eval(json_data["reply"])
            if reply["next_step"] == "Infer":
                self.append_message(chat_no, {"role": "assistant", "content": f"""当前答案存在问题，请进行反思纠错 """})
            return await self.exec0(chat_no)
        elif json_data["step"] == "Answer":
            return json_data
        if self.current_step == self.max_step:
            self.current_step = 1
            return json_data

    async def exec_code(self, code: str):
        return await self.execute_with_imports(code, {})

    async def execute_with_imports(self, code, params):
        local_vars = {}
        try:
            exec(code, {}, local_vars)
            if params:
                local_vars.update(params)
            return {"code": 0, 'result': local_vars.get('result', None), 'error': None}
        except Exception as e:
            return {"code": -1, 'result': None, 'error': str(e)}


instance = MathConversationAgent()

