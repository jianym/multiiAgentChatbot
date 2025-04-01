import base64
import os
import time

import aiofiles
from agent.AgentTool import Tool
from agent.model.DeepseekModel import llm
import config
from aiopath import AsyncPath
import json
class FileSystemTool(Tool):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = ""
        self.basePath = "tmp"

    def getPrompt(self,messageNo=None):
        content = """
        你是一名文件系统管理助手，你的目标是用户问题调用文件管理工具完成用户关于查找文件或目录等问题
        
        你按照如下步骤进行工作:
             1. 根据用户问题判断当前用户的意图。
             2. 调用相关工具传入相关参数
             3. 结合工具返回的信息，给出最终回复答案
             4. 将最终答案返回成json格式数据

        基本信息:
        {self.baseInfo}
         
        返回json格式:
        {"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name": <string>,"args": <list>}

        返回值说明:
          - `code`：0 -> 执行成功
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `reply`:  提供问题的最终回复信息
          - `tool_name`: 调用工具的名称
          - `args`: 调用工具所需的参数列表
          
        可调用工具信息:
          - `find(fileName: str)`: 通过文件名匹配相关文件,支持*号通配符，返回文件信息
            - `fileName`: 要查找的文件,支持*号通配符，不能为空和不能只是*号
          - `dir(path: str)`: 查找路径下所有文件及目录，返回文件及目录信息
            - `path`: 要查找的路径，可以为空字符串
          - `writeAndDownFile` : (fileName: str,content: str) : 写入并下载文件
            - `fileName` : 文件名，可以为空，如果没有根据内容生成
            - `content` : 文件内容，必需
          - `writeFile(self,fileName: str,content: str,mode='w')` : 写入文件，返回文件地址
            - `fileName` : 文件名，可以为空，如果没有根据内容生成
            - `content` : 文件内容，必需
          - `downFile(filePath: str)` : 下载文件
            - `filePath` : 文件地址
          - `readFile(filePath)` : 读取文件，返回文件内容
            - `filePath` : 文件地址
          - `deleteFile(filePath)` : 删除文件
            - `filePath` : 文文件地址
        """
        message = {"role": "system", "content": content}
        return message

    def queryDesc(self) -> str:
        desc = """
        FileSystemTool -> 这是一个文件系统管理助手，用于在文件相关操作，可以使用的工具如下:
          - `find(fileName: str)`: 通过文件名匹配相关文件,支持*号通配符，返回文件信息
            - `fileName`: 要查找的文件,支持*号通配符，不能为空和不能只是*号
          - `dir(path: str)`: 查找路径下所有文件及目录，返回文件及目录信息
            - `path`: 要查找的路径，可以为空字符串
          - `writeAndDownFile` : (fileName: str,content: str) : 写入并下载文件
            - `fileName` : 文件名，可以为空，如果没有根据内容生成
            - `content` : 文件内容，必需
          - `writeFile(self,fileName: str,content: str,mode='w')` : 写入文件，返回文件地址
            - `fileName` : 文件名，可以为空，如果没有根据内容生成
            - `content` : 文件内容，必需
          - `downFile(filePath: str)` : 下载文件
            - `filePath` : 文件地址
          - `readFile(filePath)` : 读取文件，返回文件内容
            - `filePath` : 文件地址
          - `deleteFile(filePath)` : 删除文件
            - `filePath` : 文文件地址
        """
        return desc

    def queryName(self) -> str:
        return "FileSystemTool"

    async def action(self, messageNo: str, jsonData: dict):
        if jsonData["code"] != 0:
            return jsonData
        if jsonData["tool_name"] == "find":
            self.toolData = await self.find(jsonData["args"][0])
        elif jsonData["tool_name"] == "dir":
            self.toolData = await self.dir(jsonData["args"][0])
        elif jsonData["tool_name"] == "writeAndDownFile":
            self.toolData = await self.writeAndDownFile(messageNo,jsonData["args"][0],jsonData["args"][1])
        elif jsonData["tool_name"] == "writeFile":
            self.toolData = await self.writeAndDownFile(messageNo, jsonData["args"][0], jsonData["args"][1])
        elif jsonData["tool_name"] == "downFile":
            self.toolData = await self.downFile(messageNo, jsonData["args"][0])
        elif jsonData["tool_name"] == "readFile":
            self.toolData = await self.readFile(messageNo, jsonData["args"][0])
        elif jsonData["tool_name"] == "deleteFile":
            self.toolData = await self.deleteFile(jsonData["args"][0],messageNo)
        return {"code": 0,"reply": json.dumps(self.toolData)}

    async def find(self,fileName: str):
        # 创建 AsyncPath 对象
        directory = AsyncPath(config.OS_BASE_PATH)
        files = []
        # 遍历目录
        async for item in directory.rglob(fileName):
            stat = await item.stat()
            # 根据判断进行分类
            if await item.is_symlink():
                fileType = "符号链接"
            elif await item.is_dir():
                fileType = "文件夹"
            else:
                fileType = "文件"

            files.append({"名称": item.name,
                          "文件类型": fileType,
                          "大小": stat.st_size, "创建时间": time.ctime(stat.st_ctime),
                          "更新时间": time.ctime(stat.st_mtime)})
        return files

    async def dir(self,path=""):
        files = []
        directory = AsyncPath(config.OS_BASE_PATH + path)
        # 查看指定目录下的文件和文件夹
        async for item in directory.iterdir():
            stat = await item.stat()
            # 根据判断进行分类
            if await item.is_symlink():
                fileType = "符号链接"
            elif await item.is_dir():
                fileType = "文件夹"
            else:
                fileType = "文件"


            files.append({"名称": item.name,"文件类型": fileType, "大小": stat.st_size,"创建时间": time.ctime(stat.st_ctime),"更新时间": time.ctime(stat.st_mtime)})

        return files


    async def deleteFile(self,filePath: str,messageNo: str):
        currentPath = os.path.join(config.OS_BASE_PATH, messageNo)
        filePath = os.path.abspath(os.path.join(currentPath, filePath))
        if os.path.commonpath([filePath, currentPath]) != currentPath:
            return False

        if os.path.exists(filePath):  # 先检查文件是否存在
            os.remove(filePath)
            return True
        else:
            return False

    async def writeAndDownFile(self,messageNo: str,fileName: str,content: str,mode='w'):
        Tool.downFile[messageNo] = await self.writeFile(messageNo,fileName, content,mode)

    async def writeFile(self,messageNo: str,fileName: str,content: str,mode='w'):
        currentPath = os.path.join(config.OS_BASE_PATH, messageNo)
        filePath = os.path.abspath(os.path.join(currentPath, self.basePath,fileName))
        if os.path.commonpath([filePath, currentPath]) != currentPath:
            return ""

        directory = os.path.dirname(filePath)  # 获取文件所在目录
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        async with aiofiles.open(filePath, mode=mode) as file:
            await file.write(content)
        return "/" + self.basePath + "/" + fileName

    async def downFile(self,messageNo: str,filePath: str):
        currentPath = os.path.join(config.OS_BASE_PATH, messageNo)
        filePath = os.path.abspath(os.path.join(currentPath, filePath))
        if os.path.commonpath([filePath,currentPath]) != currentPath:
            return False

        if os.path.exists(filePath):
            Tool.downFile[messageNo] = filePath
            return True
        else:
            return False

    async def readFile(self,messageNo: str,filePath: str):
        currentPath = os.path.join(config.OS_BASE_PATH, messageNo)
        filePath = os.path.abspath(os.path.join(currentPath,filePath))
        if os.path.commonpath([filePath,currentPath]) != currentPath:
           return ""

        if os.path.exists(filePath):
            async with aiofiles.open(filePath, mode='r') as file:
                content = await file.read()
                # 如果是图片、音频或视频文件，进行Base64编码
                if filePath.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mkv', 'mp3', 'wav', 'flac')):
                    return base64.b64encode(content).decode('utf-8')
                else:
                    return content  # 如果是文本文件，解码为UTF-8字符串
        return ""


instance = FileSystemTool()


