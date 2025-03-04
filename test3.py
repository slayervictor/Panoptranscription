from moviepy.audio.io.AudioFileClip import AudioFileClip

# Indsæt din inputfil her
input_file = "temp.mp3"
output_file = "output.mp3"

# Indlæs lydfilen
audio = AudioFileClip(input_file)

# Klip de første 15 minutter (900 sekunder)
audio_cut = audio.subclipped(0, 900)

# Gem den nye fil
audio_cut.write_audiofile(output_file, codec="mp3")

print(f"Ny lydfil gemt som: {output_file}")