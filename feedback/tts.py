import asyncio
import edge_tts
from pydub import AudioSegment
import simpleaudio as sa
from io import BytesIO

async def speak(text):
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    byte_stream = BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            byte_stream.write(chunk["data"])

    byte_stream.seek(0)
    audio = AudioSegment.from_file(byte_stream, format="mp3")
    raw_data = audio.raw_data

    play_obj = sa.play_buffer(
        raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )
    play_obj.wait_done()

# asyncio.run(speak("你好，我是语音助手"))