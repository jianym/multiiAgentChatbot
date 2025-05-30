import ast
from agent.agent_node import AgentNode
from agent.model.DeepseekModel import llm
from agent.app.conversation_app_agent_modules.search_agent import instance as search_instance



class DeepReSearchAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = ""
        self.max_step = 8
        self.current_step = 0

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名深度搜索助手，你的目标严格遵守执行流程回答用户问题。

        基本信息:
            {self.get_context_data(chat_no, "baseInfo")}

        可调用工具:
          - `info_search(questions: list)`: 对信息进行检索，返回检索结果
            - `questions`: 需要检索问题的列表 -> [{{ "question":<string>,"retrieval_method":<string> }}]
                - `question`: 需要检索的问题
                - `retrieval_method`: 问题的检索方式
                     - web_search: 从网络上搜索信息
            

        你必须严格按照如下步骤流程执行，不可跳过中间步骤:
            1. infer: 理解用户意图，给出用户的真正意图并一步一步思考解决用户问题的解决方案（应包含需要检索的所有信息（应包含检索信息的相关细节）列表及检索方式，以及需要检索这些信息的原因）
            2. retrieval: 根据解决方案列出需要的检索的所有信息列表及信息的检索方式,选择相关工具传入相关参数进行信息检索
            3. answer: 给出一个结构完整，格式清晰，内容充实，易于阅读的最终答案
            
        解决方案例子:
           用户问题: 一周后考虑从沈阳去北京
           解决方案: 
                1.首先获取一周后的具体时间
                2.检索一周后北京的天气情况，检索方式网络检索
                3.检索一周后沈阳到北京的车票，检索方式网络检索
                4.检索北京的相关景点及城市特色，检索方式网络检索

        问题及子问题内容约束:
             1. 用户问题中包含如昨日，明天，后天，前天等可以计算到某个时间，应根据当前时间进行计算到具体的时间（年月日十分秒等）
             2. 用户问题中包含的时间，如最新，近年来等这些无法具体到某一时间点的，无需转换成具体时间
             3. 需要检索的信息必须描述全面，详细
             

        最终答案reply内容约束:
            1.返回结果的内容信息应可能方便溯源
              - 如果引用的内容本身包含来源链接，则使用原引用来源链接， 使用 [源](URL) 语法来插入超链接，确保用户能够直接访问原始内容
              - 如果引用部分涉及基本的数据支撑和严谨性且没有具体的来源信息，则提出相关问题通过网络搜索工具确定信息的可靠性和来源链接
              - 可以在引用部分增加具体的 发布日期，以便用户了解信息的时效性
            2.尽可能多的返回与查询问题相关的信息（尽可能返回细节信息）
              - 提供 背景信息、技术细节、实施步骤、案例分析、对比分析、数据支撑、溯源信息、程序代码等内容。
              - 如果有多个相关因素或选项，要分别列出并给出权衡，帮助用户做出决策。
              - 如果有可能，举例说明或提供图表来辅助理解
            3.最后可以给出基于返回结果，给出当前问题的引申问题

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
          - `reply`: 每个步骤对应
              - infer: 字符串，用户真实意图及解决方案（应包含需要检索的信息列表及检索方式，以及需要检索这些信息的原因）
              - retrieval: 字段描述 -> {{"tool_name":<string>,"args": <list>}}, 输出需要调用的工具 
                   - `tool_name` -> 工具名称
                   - `args` -> 工具所需的参数列表
              - answer: 字符串，应为markdown纯字符串，输出最终答案
         """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
         DeepReSearchAgent -> 这是一个基于深度搜索的问答Agent，用更长的时间和更多的检索来源 (网络检索和知识库检索) 来保证回答问题的准确性和全面性，可以用于对回答对严谨性，准确性，权威性，全面性有更高要求的问题，返回基于深度检索的问题答案
         """
        return desc

    def query_name(self) -> str:
        return "DeepReSearchAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["step"] == "infer":
            self.append_message(chat_no,{"role": "user", "content": f"""已完成推理思考，执行retrieval，进行信息检索"""})
            return await self.exec(chat_no)
        if json_data["step"] == "retrieval":
            reply = ast.literal_eval(json_data["reply"])
            search_results = []
            for arg in reply["args"]:
                search_result = await self.web_search(chat_no,arg["question"])
                search_result = str(search_result)
                search_results.append(search_result)
            self.append_message(chat_no,{"role": "user", "content": f"""已完成检索，给出最终答案，工具搜索结果: {search_results}"""})
            return await self.exec(chat_no)
        return json_data

    # async def info_search(self,chat_no, search_datas):
    #     for search_data in search_datas:
    #         return await self.web_search(chat_no, search_data)

    async def web_search(self,chat_no: str, query) -> list:
        web_result = []
        search_instance.append_message(chat_no, {"role": "user", "content": query})
        response = await search_instance.exec(chat_no)
        if response and response["code"] == 0:
               web_result.append(response["reply"])
        return web_result


instance = DeepReSearchAgent()

