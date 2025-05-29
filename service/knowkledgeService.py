import asyncio
import io
import json
import time
import uuid

import docx as docx
import fitz as fitz
import subprocess

import pdfplumber
from fastapi import File
from agent.model.BgeModel import bgeModel
from dao.KnowledgeMilvusDao import instance
import config
import re
from agent.model.DeepseekModel import llm
from agent.model.SpacyModel import extract_entity_relation_triples


class KnowledageService:

    async def extract(self, file: File, chatNo: str):
        if file.filename.endswith(".txt"):
            text = self.read_txt(file.file)
        elif file.filename.endswith(".pdf"):
            text = self.read_pdf(file.file)
        elif file.filename.endswith(".docx"):
            text = self.read_docx(file.file)
        elif file.filename.endswith(".doc"):
            text = self.read_doc(file)
        else:
            return "unknown"

        if text:
            cleaned_text = self.clean_text_for_rag(text)
            content = f"""
            你是一名简历提取专家，你可以在简历中提取姓名，年龄，联系电话，联系邮箱，学校，专业，过往公司，项目经验，求职意向
            
            简历内容:
            {cleaned_text}
            
            返回json格式的数据:
            {{ "name":<string>,"age": <string>,"phone":<string>,"email":<string>,"school":<string>,"major":<string>,"company":<list>,"project": <list>,"desired_position": <string>}}
            
            返回字段说明:
              - 'name' :  姓名
              - 'age' :  年龄
              - 'phone' :  联系电话
              - 'email' :  联系邮箱
              - 'school' :  大学学校
              - 'major' :  大学专业
              - 'company' :  过往公司
              - 'project' :  项目经验
              - 'desired_position' : 求职意向

            """
            response = await llm.acall(json.dumps([{"role":"user","content": content}]))
            response_data = response["choices"][0]["message"]["content"]
            return json.loads(response_data)

    async def store(self, file: File, chatNo: str):

        if file.filename.endswith(".txt"):
            text = self.read_txt(file.file)
        elif file.filename.endswith(".pdf"):
            text = self.read_pdf(file.file)
        elif file.filename.endswith(".docx"):
            text = self.read_docx(file.file)
        elif file.filename.endswith(".doc"):
            text = self.read_doc(file)
        else:
            return "unknown"

        instance.createMilvus()
        if text:
            cleaned_text = self.clean_text_for_rag(text)
            chunks = self.process_paragraphs_with_context(cleaned_text)
            for item in chunks:
                for senItem in item["sentences"]:
                    embedding = bgeModel.getEmbedding(senItem)
                    data = [{"dense_vector": embedding, "text": senItem, "chat_no": chatNo, "user_id": "1",
                             "para": item["para"], "uuid_str": item["uuid"],
                             "create_time": int(time.time()), "file_path": "/1/knowledge/" + file.filename}]
                    instance.insertMilvus(data)

    def split_text_sliding_window(self, text, window_size=512, stride=128):
        """滑动窗口分割文本"""
        chunks = [text[i:i + window_size] for i in range(0, len(text), stride)]
        return chunks

    async def searchRAG(self, query: str, chatNo: str, threshold=0.8):
        filteredResults = []
        instance.createMilvus()
        searchResult = instance.search(query, [bgeModel.getEmbedding(query)], chatNo, "1",radius=threshold)

        if len(searchResult) > 0:
            seen_uuids = set()
            for result in searchResult[0]:
                # if result["distance"] < threshold:
                uuid = result["entity"]["uuid_str"]
                if uuid not in seen_uuids:
                    seen_uuids.add(uuid)
                    filteredResults.append(
                        {"para": result["entity"]["para"], "file_path": result["entity"]["file_path"]})
        if filteredResults:
            # map_result = await self.map(query, filteredResults, "file_path", 2048)
            # if map_result:
            return await self.summary_llm(query, filteredResults)
        return None

    async def map(self, query: str, contents: list, map_key: str, max_size: int):
        result = []
        query_map = {}
        for content in contents:
            key = content[map_key]
            para = query_map.get(key, None)
            if para:
                para = query_map[key] + '\n' + content["para"]
            else:
                para = content["para"]
            query_map[key] = para
            if len(para) > max_size:
                map_result = await self.summary_llm(query, {"text": para, "source": key})
                if map_result:
                    result.append(map_result)
                query_map.pop(key, None)
        for key, value in query_map.items():
            map_result = await self.summary_llm(query, {"text": value, "source": key})
            if map_result:
                result.append(map_result)
        return result

    async def summary_llm(self, query: str, knowledge_data):
        map_content = f"""
             你是一名知识库问题助手，你根据知识库内容，回答用户问题，如果知识库内容不能够回答用户问题，返回不知道

             用户问题:
             {query}

             知识库内容:
             {knowledge_data}
            
            返回结果reply内容约束:
                1.返回结果中引用知识库部分必须标记出知识库文件链接，方便溯源
                    - 使用 [源](URL) 语法来插入超链接，确保用户能够直接访问原始内容
               
             返回json格式的数据:
             {{ "code": <int>, "reply":<string> }}

                 code -> 如果知识库里的内容可以回答用户的问题返回0，否则返回1
                 reply -> 问题答案，如果知识库内容不能够回答用户问题则答案为不知道
             """
        res = await llm.acall(json.dumps([{"role": "user", "content": map_content}]))
        response_data = res["choices"][0]["message"]["content"]
        json_data = json.loads(response_data)
        if json_data["code"] == 0:
            return json_data["reply"]

        return None

    def read_txt(self, file: File):
        """读取 TXT 文件"""
        return file.read().decode("utf-8")

    def read_pdf(self, file: File):
        all_text = []
        file.seek(0)
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):

                # 获取所有的内容块（text+table）
                elements = []

                # 添加文本块，extract_words() 返回 dict，top 是 y0 坐标
                for word in page.extract_words():
                    elements.append({
                        'type': 'text',
                        'y0': word['top'],
                        'text': word['text']
                    })

                # 添加表格块，find_tables() 返回 Table 对象，带 bbox 信息
                tables = page.find_tables()
                for table in tables:
                    y0 = table.bbox[1]
                    elements.append({
                        'type': 'table',
                        'y0': y0,
                        'table': table.extract()
                    })

                # 按 y 坐标从小到大排序（从上到下）
                elements.sort(key=lambda x: float(x['y0']))

                # 输出内容
                for item in elements:
                    if item['type'] == 'text':
                        all_text.append(item['text'])
                    else:
                        for row in item['table']:
                            all_text.append('\t'.join(row))  # 输出整行表格内容

        return '\n'.join(all_text)

    def read_docx(self, file: File):
        """读取 DOCX 文件"""
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    def read_doc(self, file):
        try:
            # 使用 subprocess.run 调用 catdoc
            result = subprocess.run(['catdoc', config.OS_BASE_PATH + "/knowledge/" + file.filename],
                                    capture_output=True, text=True)

            # 获取 catdoc 输出的文本内容
            text = result.stdout

            # 如果需要进一步处理文本内容（比如分段），你可以根据行或其他规则拆分
            paragraphs = text.split('\n')  # 使用换行符分段

            return "\n".join(paragraphs)

        except FileNotFoundError:
            print("catdoc command not found. Please install it first.")
            return None

    def clean_text_for_rag(self, text):
        text = self.clean_linebreaks(text)
        text = self.normalize_spaces(text)
        text = self.remove_chinese_ocr_spaces(text)
        return text

    def clean_linebreaks(self, text):
        # 使用正则匹配：行末没有标点符号并且有换行符的地方
        text = re.sub(r"([^\n。！？！\.\?!;])\n", r"\1 ", text)
        return text

    def normalize_spaces(self, text):
        # 把连续空格变成一个
        # text = re.sub(r'\s{2,}', ' ', text)
        return re.sub(r"[ \t]+", " ", text).strip()

    # 中文特殊情况（OCR 有空格）

    def remove_chinese_ocr_spaces(self, text):
        # 识别中文之间的空格，如：“北 京 大 学”
        return re.sub(r'(?<=[\u4e00-\u9fff]) (?=[\u4e00-\u9fff])', '', text)

    def process_paragraphs_with_context(self, text):
        paragraphs = self.split_mixed_paragraphs(text)
        result_all, tmp_paragraphs, tmp_buffer = [], "", []

        for i, para in enumerate(paragraphs):
            para = para.strip()
            tmp_paragraphs = f"{tmp_paragraphs}\n{para}" if tmp_paragraphs else para
            tmp_buffer.append(para)
            if len(tmp_paragraphs.encode('utf-8')) > 1024:
                result_all.append({
                    "uuid": str(uuid.uuid4()).replace("-", ""),
                    "sentences": self.split_sentences_zh_en(tmp_paragraphs),
                    "para": (
                            '\n'.join(tmp_buffer[:-1]).encode('utf-8')[-512:] +
                            tmp_paragraphs.encode('utf-8') +
                            (paragraphs[i + 1].encode('utf-8')[:512] if i + 1 < len(paragraphs) else b'')
                    ).decode('utf-8', errors='ignore')
                })
                tmp_paragraphs, tmp_buffer = "", []

        if tmp_paragraphs:
            result_all.append({
                "uuid": str(uuid.uuid4()).replace("-", ""),
                "sentences": self.split_sentences_zh_en(tmp_paragraphs),
                "para": (
                        '\n'.join(tmp_buffer[:-1]).encode('utf-8')[-512:] +
                        tmp_paragraphs.encode('utf-8')
                ).decode('utf-8', errors='ignore')
            })
        return result_all

    def split_sentences_zh_en(self, text):
        # 1. 处理中文标点符号后的句子分割：如句号、问号、感叹号
        text = re.sub(r'([。！？])([^”’"\'])', r"\1\n\2", text)  # 中文标点后的换行

        # 2. 处理英文标点符号后的句子分割：如句号、问号、感叹号
        text = re.sub(r'([.?!])(\s+|\n|\t)*', r"\1\n", text)  # 英文标点后的换行

        # 3. 处理中文标点符号后的引号情况
        text = re.sub(r'([。！？][”’"\'])', r"\1\n", text)  # 中文标点符号后有引号的换行

        # 4. 处理长句子没有结束符的情况，通过分号等标点符号进行智能分割
        text = re.sub(r'([；])([^，。！？!?])', r"\1\n\2", text)  # 分号后的换行

        text = re.sub(r'([;])([^，。！？!?])', r"\1\n\2", text)  # 分号后的换行

        # 4. 去除多余的空白字符
        text = text.strip()

        # 5. 按换行符分割句子，并去除空行
        return [s.strip() for s in text.split('\n') if s.strip()]

    def split_mixed_paragraphs(self, text):

        lines = text.splitlines()
        # lines = [p.strip() for p in text.split('\n') if p.strip()]

        paragraphs = []
        tmp_para = ""

        for i in range(len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            tmp_para += line

            # 是否是最后一行
            if i == len(lines) - 1:
                paragraphs.append(tmp_para.strip())
                break

            next_line_raw = lines[i + 1]
            next_line = next_line_raw.lstrip()
            next_indent_len = len(next_line_raw) - len(next_line)

            # 当前行以中文或英文的段末标点结尾
            if re.search(r'[。！？；…\.\?!;]$', line) and next_indent_len >= 2:
                paragraphs.append(tmp_para.strip())
                tmp_para = ""

        # 收尾处理
        if tmp_para:
            paragraphs.append(tmp_para.strip())

        return paragraphs


knowledageServiceInstance = KnowledageService()
