import asyncio
import os
import threading
import speech_recognition as sr
from agent.query_route_agent import queryRoute
from feedback.tts import speak
r = sr.Recognizer()

class AudioThread(threading.Thread):

    def __init__(self, cam_index=0):
        super().__init__(daemon=True)  # 设置为守护线程，主线程退出时自动关闭

    def stop(self):
        self.running = False

    def setChatNo(self,chatNo: str):
        self.messageNo = chatNo


    async def handler(self,text):
        jsonData = await queryRoute.start(self.messageNo, text, True)
        print("识别结果：", jsonData)
        await speak(jsonData["reply"])

    def run(self):
        self.running = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # 设置事件循环
        while self.running:
            with sr.Microphone() as source:
                print("请开始说话：")
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio, language='zh-CN')
                    if text and len(text) > 0:
                        task = loop.create_task(self.handler(text))
                        loop.run_until_complete(task)
                except sr.UnknownValueError:
                    print("无法识别语音")
                except sr.RequestError as e:
                    print(f"请求出错：{e}")
                except Exception as e:
                    print(f"发生错误：{e}")

audio_thread = AudioThread()


# import numpy as np
# import sounddevice as sd
# from funasr import AutoModel
# import webrtcvad
# import time
#
# # 初始化参数
# chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
# encoder_chunk_look_back = 4  # 编码器的回溯块数
# decoder_chunk_look_back = 1  # 解码器的回溯块数
#
# # 加载模型
# model = AutoModel(model="paraformer-zh-streaming")
#
# chunk_stride = chunk_size[1] * 960  # 600ms的块步长
# buffer = None  # 麦克风数据缓存
# cache = {}  # FunASR缓存
# transcription_result = []  # 存储转录结果
# last_output_time = time.time()  # 上次输出的时间
# output_interval = 2  # 每2秒输出一次结果
#
# # 初始化VAD
# vad = webrtcvad.Vad(0)  # 设置VAD模式，1为最温和模式，0为最严格模式
#
# # 设置静默的阈值，单位为秒
# silence_threshold = 2  # 1.5秒静默时间，认为当前话结束
#
# last_speech_time = time.time()  # 上次检测到语音活动的时间
#
# #
# # def is_speech(audio_chunk, sample_rate=48000):
# #     # 每个帧的时长为10ms，计算每帧的大小
# #     frame_duration = 10  # 每帧时长为10ms
# #     frame_size = int(sample_rate * frame_duration / 1000)  # 每帧的大小，10ms对应的帧大小
# #
# #     # 将音频分帧，每帧大小为frame_size
# #     num_frames = len(audio_chunk) // frame_size  # 分割成多个帧
# #     for i in range(num_frames):
# #         start = i * frame_size
# #         end = start + frame_size
# #         frame = audio_chunk[start:end]
# #
# #         # 确保帧数据是单声道、16位PCM格式
# #         if len(frame) == frame_size:
# #             # 注意：webrtcvad要求传入字节流数据
# #             if vad.is_speech(frame.tobytes(), sample_rate):
# #                 print(f"检测到语音帧，帧开始时间: {start / sample_rate:.2f}秒")  # 调试语音帧
# #                 return True
# #     return False
#
# is_speech = True
# def callback(indata, frames, time_info, status):
#     global buffer, cache, transcription_result, last_output_time, last_speech_time,is_speech
#     if buffer is None:
#         buffer = indata
#     else:
#         buffer = np.append(buffer, indata)
#
#     # 如果缓冲区数据还不够，直接返回
#     if len(buffer) < chunk_stride * 3:
#         return
#
#     # 切分块数据
#     chunk = np.array([buffer[i] for i in range(0, chunk_stride * 3) if i % 3 == 0])
#
#     # 生成推理结果
#     res = model.generate(
#         input=chunk,
#         cache=cache,
#         is_final=False,
#         chunk_size=chunk_size,
#         encoder_chunk_look_back=encoder_chunk_look_back,
#         decoder_chunk_look_back=decoder_chunk_look_back,
#     )
#
#     # 打印每次生成的结果
#     # print(f"Model output: {res}")
#
#     # 处理返回的文本
#     if isinstance(res, list) and len(res) > 0:
#         text = res[0].get('text', '')  # 获取文本，避免KeyError
#         if text:
#             is_speech = True
#             transcription_result = transcription_result+text  # 如果有文本，添加到转录结果
#             print(transcription_result)
#         else:
#             is_speech = False
#             print("No transcription result yet.")
#
#     # 更新缓存
#     buffer = buffer[chunk_stride * 3:]  # 保持缓冲区大小
#     # 判断是否有语音活动（通过VAD）
#     if is_speech:
#         last_speech_time = time.time()  # 使用 time.time() 获取当前时间
#     else:
#         # 如果没有语音活动，检查是否已经超过静默阈值
#         if time.time() - last_speech_time > silence_threshold:
#             # 如果静默超过阈值，认为当前话已经结束
#             print("当前话语结束")
#             print("转录结果: ", transcription_result)  # 输出当前积累的转录内容
#             transcription_result = ""  # 清空累积的结果
#             buffer = buffer[chunk_stride * 3:]  # 清空缓冲区，准备下次推理
#             return
#
#
#
#
# # 启动音频流
# with sd.InputStream(device=0, samplerate=48000, callback=callback):
#     print("语音输入已启动，请开始说话...")
#     sd.sleep(600000)  # 运行10分钟，确保程序可以继续监听