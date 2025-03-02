import whisper
import torch, torchaudio, torchvision
import openai
import imageio_ffmpeg as ffmpeg

ffmpeg_path = ffmpeg.get_ffmpeg_exe()  # Gets the bundled ffmpeg executable
print(f"Using FFmpeg from: {ffmpeg_path}")

API_KEY = "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"
API_WHISPER_MODEL = "whisper-1"
GPU_MODEL = "small"
DEVICE = "cuda"  # Use lowercase for consistency

def do_transcribe(file):
    """Transcribes audio using GPU (Whisper) if available, otherwise uses OpenAI API."""
    device = "cuda" if torch.cuda.is_available() else "api"
    print("Device found:", device)

    if device == "cuda":
        model = whisper.load_model(GPU_MODEL, device="cuda")
        result = model.transcribe(file, verbose=True, language="en")
        return "".join(seg["text"] for seg in result["segments"])
    
    elif device == "api":
        if API_KEY is None:
            raise ValueError("API key is missing. Set OPENAI_API_KEY as an environment variable.")
        
        with open(file, "rb") as audio_file:
            response = openai.Audio.transcribe(
                model=API_WHISPER_MODEL,
                file=audio_file,
                response_format="text"
            )
        return response

    else:
        raise RuntimeError("Transcription failed: Unknown device detected.")

print(do_transcribe("temp.wav"))