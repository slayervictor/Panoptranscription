import whisper

model = whisper.load_model("large")
result = model.transcribe("temp.wav", language="da")
print(result["text"])
