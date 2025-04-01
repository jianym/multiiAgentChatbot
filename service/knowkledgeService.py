import time

import docx as docx
import fitz as fitz
import subprocess

from fastapi import File
from agent.model.BgeModel import bgeModel
from dao.KnowledgeMilvusDao import instance
import config
class KnowledageService:

     def store(self,file: File,chatNo: str):

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
         chunks = self.split_text_sliding_window(text)
         for item in chunks:
             embedding = bgeModel.getEmbedding(item)
             data = [{"vector": embedding, "text": item,"chat_no": chatNo,"user_id":"1","create_time": int(time.time()), "file_path": "/1/knowledge/" + file.filename}]
             instance.insertMilvus(data)

     def searchRAG(self,query: str,chatNo: str,threshold=1):
         filteredResults = []
         searchResult = instance.search([bgeModel.getEmbedding(query)],chatNo,"1")
         if len(searchResult) > 0:
            filteredResults = [result["entity"]["text"] for result in searchResult[0] if result["distance"] < threshold]

         return filteredResults




     def read_txt(self,file: File):
         """读取 TXT 文件"""
         return file.read().decode("utf-8")

     def read_pdf(self,file: File):
         """读取 PDF 文件"""
         pdf_document = fitz.open(stream=file.read(), filetype="pdf")
         text = "\n".join([page.get_text() for page in pdf_document])
         return text


     def read_docx(self,file: File):
         """读取 DOCX 文件"""
         doc = docx.Document(file)
         text = "\n".join([para.text for para in doc.paragraphs])
         return text

     def read_doc(self, file):
         try:
             # 使用 subprocess.run 调用 catdoc
             result = subprocess.run(['catdoc',config.OS_BASE_PATH +"/knowledge/"+file.filename], capture_output=True, text=True)

             # 获取 catdoc 输出的文本内容
             text = result.stdout

             # 如果需要进一步处理文本内容（比如分段），你可以根据行或其他规则拆分
             paragraphs = text.split('\n')  # 使用换行符分段

             return "\n".join(paragraphs)

         except FileNotFoundError:
             print("catdoc command not found. Please install it first.")
             return None

     def split_text_sliding_window(self,text, window_size=512, stride=128):
          """滑动窗口分割文本"""
          chunks = [text[i:i + window_size] for i in range(0, len(text), stride)]
          return chunks

knowledageServiceInstance = KnowledageService()