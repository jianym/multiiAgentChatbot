import requests
from bs4 import BeautifulSoup
import pdfplumber
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chardet

def pdfDoucment(content,link):
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # 处理 PDF 文件
    with pdfplumber.open(BytesIO(content)) as pdf:
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()

            # 清理文本
        pdf_text = " ".join(pdf_text.split())
        splitted_text = splitter.split_text(pdf_text)
        title = "PDF Document"

        # 创建文档对象并添加到列表
        for text in splitted_text:
            docs.append({"pageContent": text, "title":  title,"url": link})
    return docs

def htmlDocument(content,link):
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # 处理 HTML 文件
    soup = BeautifulSoup(content, 'html.parser')

    # 去除所有 <a> 标签及其 href 属性
    for a_tag in soup.find_all('a'):
        a_tag.decompose()  # 去除 <a> 标签及其内容

    # 获取纯文本，去除所有标签
    html_text = soup.get_text(separator=' ', strip=True)

    html_text = " ".join(html_text.split())  # 去除多余空格

    # 使用文本拆分器进行拆分
    splitted_text = splitter.split_text(html_text)

    # 获取 HTML 标题
    title_tag = soup.find('title')
    title = title_tag.string if title_tag else link

    # 创建文档对象并添加到列表
    for text in splitted_text:
        docs.append({"pageContent": text, "title":  title,"url": link})

    return docs

def getDocumentsFromLinks(links):
    docs = []
    for link in links:
        # 确保链接以 http:// 或 https:// 开头
        if not link.startswith('http://') and not link.startswith('https://'):
            link = f'https://{link}'

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com'
            }
            # 请求链接内容
            res = requests.get(link, headers=headers)
            # res.encoding = 'utf-8'
            res.raise_for_status()  # 如果请求失败，抛出异常
            content_type = res.headers['Content-Type']
            # 使用 chardet 自动检测响应的编码
            detected_encoding = chardet.detect(res.content)['encoding']
            if 'pdf' in content_type:
                 docs.extend(pdfDoucment(res.content, link))
            else:
                 res.encoding = detected_encoding  # 设置正确的编码
                 docs.extend(htmlDocument(res.text, link))

        except Exception as e:
            print(f"An error occurred while getting documents from link {link}: {e}")
    return docs