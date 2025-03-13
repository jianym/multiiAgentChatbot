import smtplib
# 负责构造文本
from email.mime.text import MIMEText
# 负责构造图片
from email.mime.image import MIMEImage
# 负责将多个对象集合起来
from email.mime.multipart import MIMEMultipart
from email.header import Header
from agent.AgentGraph import Node
import json
from agent.model.BaseModel import BaseModel
# SMTP服务器,这里使用163邮箱
mail_host = "smtp.qq.com"
# 发件人邮箱
mail_sender = "110714284@qq.com"
# 邮箱授权码,注意这里不是邮箱密码,如何获取邮箱授权码,请看本文最后教程
mail_license = "salvxkzkffpkbijf"
smtp_port = 587

class EmailTool(Node):

    def getPrompt(self):
        content = {"role": "system", "content":
            f"你是一名邮件发送助手，可以使用已有工具解决问题: \n"
            "你的工作职责是提取收件人邮箱，邮件主题，邮件内容并使用工具发送邮件\n"
            "如果没有提取到邮件内容可以根据上下文生成 \n"
            "如果邮件主题缺失可以从邮件内容出生成 \n"
            "返回json格式:\n"
            "{\"status\":2,\"reply\":\"...\",\"tool_use\": true, \"tool_name\":tool_name,\"args\": [...]}} \n"
            "返回值说明： \n"
            " status: 0 -> 收件人邮箱或邮件主题或邮件内容信息却失，需要用户补充, 2 -> 执行成功 \n" 
            " reply: status为2 -> 问题解决信息, status为0 -> 需要补充的信息 \n"
            " tool_use: true -> 需使用工具, false -> 不使用工具 \n"
            " tool_name: 工具名称 \n"
            " args: 参数列表 \n"
            "已有工具信息: \n"
            " -send(receivers: str, subject: str, content: str): receivers -> 接收人邮箱多个用逗号分隔, subject -> 邮件主题, content -> 邮件内容 \n"
        }
        return content

    def queryDesc(self) -> str:
        return "这是一个通过提取收件人邮箱，邮件主题，邮件内容进行发送email的邮件工具，调用方时应保证传递的信息包含收件人邮箱，邮件主题，邮件内容等信息"

    def queryName(self) -> str:
        return "EmailTool"

    async def exec(self, messageNo: str,llm: BaseModel) -> str:
        response = await llm.acall(json.dumps(self.messageDict[messageNo]))
        jsonData = json.loads(response)

        if jsonData["status"] == 2:
            try:
                getattr(self, jsonData["tool_name"])(*jsonData["args"])
            except Exception as e:
                print(f"错误: {e}")
                jsonData["reply"] = "邮件发送失败"

        self.reply = jsonData["reply"]
        self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})

        return json.dumps(jsonData)

    def send(self,receivers: str, subject: str, content: str):
        mm = MIMEMultipart('related')
        mail_receivers = receivers

        # 设置发送者,注意严格遵守格式,里面邮箱为发件人邮箱
        mm["From"] = mail_sender
        # 设置接受者,注意严格遵守格式,里面邮箱为接受者邮箱
        mm["To"] = receivers
        # 设置邮件主题
        mm["Subject"] = Header(subject, 'utf-8')
        # 构造文本,参数1：正文内容，参数2：文本格式，参数3：编码方式
        message_text = MIMEText(content, "plain", "utf-8")
        # 向MIMEMultipart对象中添加文本对象
        mm.attach(message_text)
        stp = smtplib.SMTP(mail_host, smtp_port)

        stp.starttls()
        # set_debuglevel(1)可以打印出和SMTP服务器交互的所有信息
        stp.set_debuglevel(1)
        # 登录邮箱，传递参数1：邮箱地址，参数2：邮箱授权码
        stp.login(mail_sender, mail_license)
        # 发送邮件，传递参数1：发件人邮箱地址，参数2：收件人邮箱地址，参数3：把邮件内容格式改为str
        stp.sendmail(mail_sender, mail_receivers, mm.as_string())  # 创建SMTP对象

        stp.quit()

instance = EmailTool()