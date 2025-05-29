from typing import List

import config
from http import HTTPStatus
# from urllib.parse import urlparse, unquote
# from pathlib import PurePosixPath
import os

os.environ["DASHSCOPE_API_KEY"] = config.QWEN_API_Key

from dashscope import ImageSynthesis,api_key

class WanxModel:

    api_url: str = config.QWEN_URL

    # 创建异步任务
    def create_async_task(self,query,size: str):
        rsp = ImageSynthesis.async_call(api_key=api_key,
                                        model="wanx2.1-t2i-turbo",
                                        prompt=query,
                                        n=1,
                                        size=size)
        # print(rsp)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))
        return rsp

    # 等待异步任务结束
    def wait_async_task(self,task):
        rsp = ImageSynthesis.wait(task)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
            picUrls = []
            for result in rsp.output.results:
                # file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                picUrls.append(result.url)
            return picUrls
                # with open('./%s' % file_name, 'wb+') as f:
                #     f.write(requests.get(result.url).content)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))
            return None

    # 获取异步任务信息
    def fetch_task_status(self,task):
        status = ImageSynthesis.fetch(task)
        print(status)
        if status.status_code == HTTPStatus.OK:
            print(status.output.task_status)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (status.status_code, status.code, status.message))

    # 取消异步任务，只有处于PENDING状态的任务才可以取消
    def cancel_task(self,task):
        rsp = ImageSynthesis.cancel(task)
        print(rsp)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output.task_status)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

    def acall(self, query: str,size) -> list[str] | None:
        print('----create task----')
        task_info = self.create_async_task(query,size)
        print('----wait task done then save image----')
        return self.wait_async_task(task_info)

wanXllm = WanxModel()



