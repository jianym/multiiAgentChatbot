import json



from agent.agent_node import AgentNode
from agent.model.DeepseekModel import llm


class ProseGenAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = ""
        self.kwargs = {"temperature": 1.5,"max_tokens": 8192}

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名散文编写助手,根据多轮对话理解用户编写散文的要求，生成散文
        
       
        你可以生成长文本内容，以满足字数要求
        你可以尽可能多的输出内容，以满足字数要求
        
        你必须按照如下流程顺序一步一步操作执行，不可跳过中间过程:
            1.根据上下文理解用户意图
            2. 生成散文的标题
            3. 生成散文的摘要
            4. 生成散文开头内容
            4. 生成7到N个散文正文段落主题
            5. 生成散文结尾内容
            
       每一个执行阶段都必须返回json格式数据
       
        一、散文的基本特征
            真实情感：散文注重抒发作者真实的思想感情，可以是对生活的感悟、对自然的热爱、对人情的观察等。
            题材自由：可以写人、写事、写景、写物，也可以写一段回忆、一种情绪，甚至是一种哲理。
            语言优美：语言讲究韵味与节奏感，富有表现力和感染力。
            结构灵活：不像小说或议论文有严格的结构，散文结构自由，但也应有内在的逻辑和连贯性。
        
        二、散文的构思与写作要点
            1.确定主题
            先明确你要表达的情感或思想，比如：孤独、希望、成长、乡愁、自然之美、人世沧桑等。
            2.选好切入角度
            是从一件小事写起？还是通过一段旅程？或者用一幅画面、一段对话作为引子？角度新颖能增强吸引力。
            3.构建意境
            散文常常追求“情景交融”的意境。可以通过描写自然景色、环境氛围来烘托情感。
            4.运用修辞
            如比喻、拟人、排比等手法可以增强文字的表现力，使情感更具感染力。
            5.情感线要清晰
            整篇文章的情感线应逐步展开，有起伏、有转折，让读者感受到情感的层层递进。
            6.收尾自然有力
            散文的结尾可以是点题、升华、回环，也可以是留白，给人回味无穷的空间。
        
        三、常见类型举例
            写景散文: 描写自然景物，寓情于景
            抒情散文: 倾诉个人情感，语言细腻感人
            叙事散文: 通过小故事或经历，抒发感悟
            哲理散文: 融合人生哲思，语言含蓄深刻
            游记散文: 写旅途中所见所感，景情交融
            
            
        基本信息:
            {self.get_context_data(chat_no, "baseInfo")}
        
        返回json格式的数据:
            {{"code":0,"reply":<string>,"title":<string>,"type":<string>,"head":<string>,"summary":<string>,"paragraphs":<list>,"tail":<string>}}

        返回值说明:
            - `code`: 0 -> 执行成功, 1 -> 执行失败
            - `reply`: 成功原因/失败原因
            - `title`: 散文标题
            - `head`: 散文开头内容
            - `type`: 散文类型
            - `summary`: 散文摘要
            - `paragraphs`: 每一个段落的主题
            - `tail`: 散文结尾内容
            

                
        """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
        """
        return desc

    def query_name(self) -> str:
        return "ProseGenAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] == 1:
            return json_data
        paragraphs = json_data["paragraphs"]
        context = {"title": json_data["title"], "summary":  json_data["summary"], "head": json_data["head"],"type": json_data["type"], "paragraphs_topic": json_data["paragraphs"],"paragraphs": [],"tail": json_data["tail"]  }
        for paragraph in paragraphs:
             paragraph_content = f"""
             你是一名散文写作助手，根据上下文信息编写当前段落主题的段落内容

             基本信息:
             {self.get_context_data(chat_no, "baseInfo")}
             
             
             一、散文的基本特征
                 真实情感：散文注重抒发作者真实的思想感情，可以是对生活的感悟、对自然的热爱、对人情的观察等。
                 题材自由：可以写人、写事、写景、写物，也可以写一段回忆、一种情绪，甚至是一种哲理。
                 语言优美：语言讲究韵味与节奏感，富有表现力和感染力。
                 结构灵活：不像小说或议论文有严格的结构，散文结构自由，但也应有内在的逻辑和连贯性。

             二、散文的构思与写作要点
                 1.确定主题
                 先明确你要表达的情感或思想，比如：孤独、希望、成长、乡愁、自然之美、人世沧桑等。
                 2.选好切入角度
                 是从一件小事写起？还是通过一段旅程？或者用一幅画面、一段对话作为引子？角度新颖能增强吸引力。
                 3.构建意境
                 散文常常追求“情景交融”的意境。可以通过描写自然景色、环境氛围来烘托情感。
                 4.运用修辞
                 如比喻、拟人、排比等手法可以增强文字的表现力，使情感更具感染力。
                 5.情感线要清晰
                 整篇文章的情感线应逐步展开，有起伏、有转折，让读者感受到情感的层层递进。
                 6.收尾自然有力
                 散文的结尾可以是点题、升华、回环，也可以是留白，给人回味无穷的空间。

             三、常见类型举例
                 写景散文: 描写自然景物，寓情于景
                 抒情散文: 倾诉个人情感，语言细腻感人
                 叙事散文: 通过小故事或经历，抒发感悟
                 哲理散文: 融合人生哲思，语言含蓄深刻
                 游记散文: 写旅途中所见所感，景情交融
            
             当前段落主题:
             {paragraph}
             
             上下文信息:
             {context}
             
             """
             prompt = [{"role":"system", "content":paragraph_content}]
             prompt.append({"role":"user","content": "生成当前段落主题下的段落内容"})
             response = await self.llm.acall(json.dumps(prompt),response_format="text",**self.kwargs)
             para = response["choices"][0]["message"]["content"]
             context["paragraphs"].append(para)

        prompt = [{"role": "user", "content": f"""
            根据上下文信息生成完整的散文内容（标题，开头，正文，结尾）
        
            基本信息:
            {self.get_context_data(chat_no, "baseInfo")}
             
             
            上下文信息:
            {context}
        
        """}]
        response = await self.llm.acall(json.dumps(prompt), response_format="text", **self.kwargs)
        content = response["choices"][0]["message"]["content"]
        return {"code": 0,"reply": content}


instance = ProseGenAgent()
