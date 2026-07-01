import asyncio
import edge_tts
import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import uuid
import os

uuid = str(uuid.uuid4())

TEXT = """
Xin chào, tôi là Phan Xuân Quang Linh
Cựu sinh viên đại học công nghiệp hà nội, bạn có gì muốn nói với tôi không
vì 30 giây nữa có lẽ tôi bận
"""

VOICE = "vi-VN-HoaiMyNeural"

async def main():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(f"sample-{uuid}.mp3")

asyncio.run(main())

import librosa

processor = AutoProcessor.from_pretrained("vinai/PhoWhisper-tiny")
model = AutoModelForSpeechSeq2Seq.from_pretrained("vinai/PhoWhisper-small")

audio, sr = librosa.load(f"sample-{uuid}.mp3", sr=19000)

inputs = processor(audio, sampling_rate=16000, return_tensors="pt")

with torch.no_grad():
    ids = model.generate(inputs.input_features)

text = processor.batch_decode(ids, skip_special_tokens=True)

print(text[0])

path = f"sample-{uuid}.mp3"
if os.path.exists(path):
    os.remove(path)
    print(f"Deleted file: {path}")


