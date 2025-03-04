from moviepy.audio.io.AudioFileClip import AudioFileClip
import os
import shutil
import whisper

def split_audio(input_file, chunk_duration=900):
    audio = AudioFileClip(input_file)
    total_duration = int(audio.duration)
    chunks = []
    
    output_dir = "output_chunks"
    
    # Ryd output-mappen, hvis den eksisterer
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    for start in range(0, total_duration, chunk_duration):
        end = min(start + chunk_duration, total_duration)
        chunk = audio.subclipped(start, end)
        output_file = os.path.join(output_dir, f"chunk_{start // 60}-{end // 60}.wav")
        chunk.write_audiofile(output_file, codec="pcm_s16le")
        chunks.append(output_file)
    
    return chunks

# Test
input_file = "temp.wav"  # Indsæt din inputfil
chunks = split_audio(input_file)
print("Følgende filer blev genereret:")
print(chunks)

model = whisper.load_model("medium")
results = []
for i in range(0, len(chunks)):
    results.append(model.transcribe(chunks[i])["text"])
    print("Chunk #"+str(i+1)+" transcribed.")
print(results)