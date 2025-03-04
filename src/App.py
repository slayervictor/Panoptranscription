from moviepy.audio.io.AudioFileClip import AudioFileClip
import customtkinter as ctk
from tkinter import filedialog
from openai import OpenAI
from moviepy import VideoFileClip, audio
import torch
import os
import time
import json
import shutil
import whisper


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.filename = "data.json"
        self.file = ""

        self.data = self.loadFromFile()

        self.title("Panoptranscription")
        self.geometry("600x700")
        self.grid_columnconfigure((0, 1), weight=1)
        self.progress = 0
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=5, column=0, padx=20, pady=10, sticky="ew", columnspan=2)
        self.progressbar.set(self.progress)  # Set initial value (0 to 1)
        
        self.progresstext = ""
        self.label = ctk.CTkLabel(self, text=self.progresstext, font=("Consolas", 16))
        self.label.grid(row=6, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

        self.API_textbox = ctk.CTkEntry(self)
        self.API_textbox.grid(row=1, column=1, padx=0, pady=20, columnspan=2,sticky="ew")
        try:
            self.chatkey = str(self.data["API_KEY"])
            self.API_textbox.insert("end",self.chatkey)
        except:
            pass

        self.labelAPI = ctk.CTkLabel(self, text="ChatGPT API Key:", font=("Consolas", 16))
        self.labelAPI.grid(row=1, column=0, padx=5, pady=20,sticky="ew")

        self.labelLang = ctk.CTkLabel(self, text="Video Language:", font=("Consolas", 16))
        self.labelLang.grid(row=2, column=0, padx=5, pady=20,sticky="ew")
        self.selectedLanguage = "da"
        self.options = ["Danish", "English"]
        self.dropdown = ctk.CTkOptionMenu(self, values=self.options, command=self.dropdownChangeLanguage)
        self.dropdown.grid(row=2, column=1, padx=20, pady=20, sticky="ew")
        try:
            self.dropdown.set(str(self.data["LANGUAGE"]))
            self.dropdownChangeLanguage(str(self.data["LANGUAGE"]))
        except:
            pass


        self.labelModel = ctk.CTkLabel(self, text="Transcription Model:", font=("Consolas", 16))
        self.labelModel.grid(row=3, column=0, padx=5, pady=20,sticky="ew")
        self.selectedModel = "large"
        self.optionsModel = ["Large (Slow, but most accurate)", "Medium (Faster, but less accurate)", "Small (English only, fastest)"]
        self.dropdownModel = ctk.CTkOptionMenu(self, values=self.optionsModel, command=self.dropdownChangeModel)
        self.dropdownModel.grid(row=3, column=1, padx=20, pady=20, sticky="ew")
        try:
            self.dropdownModel.set(str(self.data["MODEL"]))
            self.dropdownChangeModel(str(self.data["MODEL"]))
        except:
            pass
        
        self.select_file_button = ctk.CTkButton(self, text="Choose File", command=self.choose_file)
        self.select_file_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.file_entry = ctk.CTkEntry(self, width=400)
        self.file_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        try:
            self.file = str(self.data["FILE"])
            self.file_entry.insert("end",str(self.data["FILE"]))
        except:
            pass

        self.button = ctk.CTkButton(self, text="Start", command=self.button_transcribe)
        self.button.grid(row=4, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

    def dropdownChangeLanguage(self, langSelection=None):
        if langSelection == None:
            langSelection = self.dropdown.get()
        match(langSelection):
            case "English":
                self.saveToFile('LANGUAGE', "English")
                self.selectedLanguage = "en"
                self.disclaimerInstruction = "Only respond with the notes in LaTeX code. Do not respond with any natural language or formatting. "
                self.generalInstruction = " If some topics are not accurate enough in the transcription, you are welcome to write general notes on the topic. "
                self.continueInstruction = "Can you iterate on the following LaTeX math notes with information from this transcription? " + self.generalInstruction
                self.startInstruction = "Can you create LaTeX math notes from this transcription? " + self.generalInstruction
            case "Danish":
                self.saveToFile('LANGUAGE', "Danish")
                self.selectedLanguage = "da"
                self.disclaimerInstruction = "Kun responder med noterne i latex kode. Ikke responder med noget naturligt sprog eller formattering. "
                self.generalInstruction = "Hvis nogle emner ikke er akkurat nok i transkribtionen, må du gerne skrive generelle noter om emnet. "
                self.continueInstruction = "Kan du iterere på følgende LaTeX-matematiknoter med information fra denne transkription? " + self.generalInstruction
                self.startInstruction = "kan du lave latex matematik noter denne transkribtion? " + self.generalInstruction

    def dropdownChangeModel(self, modelSelection=None):
        if modelSelection == None:
            modelSelection = self.dropdownModel.get()
        match(modelSelection):
            case "Large (Slow, but most accurate)":
                self.saveToFile('MODEL', "Large (Slow, but most accurate)")
                self.selectedModel = "large"
            case "Medium (Faster, but less accurate)":
                self.saveToFile('MODEL', "Medium (Faster, but less accurate)")
                self.selectedModel = "medium"
            case "Small (English only, fastest)":
                self.saveToFile('MODEL', "Small (English only, fastest)")
                self.selectedModel = "small"

    def updateAPIKey(self,key):
        os.environ["OPENAI_API_KEY"] = key
        OpenAI.api_key = os.getenv("OPENAI_API_KEY")

    def choose_file(self): # Function to get file via file explorer
        file_selected = filedialog.askopenfilename(filetypes=[("Mp4 or Wav Files", "*.mp4;*.wav")])
        if file_selected:
            self.file = file_selected
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, self.file)
            if ".mp4" in self.file.lower() or ".wav" in self.file.lower(): 
                self.update_progress_text(f"Correct file format selected.")
            else:
                self.update_progress_text(f"Wrong file format selected.")
            self.saveToFile('FILE', self.file)

    # Update progress
    def update_progress(self, prog=1):
        self.progress += prog
        self.progressbar.set(self.progress/4)  # Update progress bar
        self.update_idletasks()

    # Update progress text
    def update_progress_text(self, _text):
        self.label.configure(text=_text)
        self.update_idletasks()

    def saveToFile(self, key, value):
        self.data = self.loadFromFile()
        
        # Save new key-value pair
        self.data[key] = value
        
        # Save the updated data to the correct file
        with open(self.filename, 'w') as file:
            json.dump(self.data, file)
        
    def loadFromFile(self):
        try:
            # Open and load data from the correct file
            with open(self.filename, 'r') as file:
                return json.load(file)
        except:
            # Return an empty dictionary if the file doesn't exist
            return {}

    def split_audio(self, input_file, chunk_duration=900):
        audio = AudioFileClip(input_file)
        total_duration = int(audio.duration)
        chunks = []

        output_dir = "output_chunks"

        # Delete all in output_chunks if not empty
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

    def transcribe(self):
        # Check if CUDA is available, otherwise fallback to CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the model on the appropriate device
        model = whisper.load_model("large").to(device)

        # Split audio into chunks
        self.chunks = self.split_audio("temp.wav")
        print("Følgende filer blev genereret:")
        print(self.chunks)

        self.results = []
        for i in range(0, len(self.chunks)):
            self.update_progress_text(f"Transcribing chunk #{i+1} of {len(self.chunks)} chunks via {device}")
            
            # Transcribe using the model on the appropriate device
            result = model.transcribe(self.chunks[i], language=self.selectedLanguage)
            
            self.results.append(result["text"])
            self.update_progress(prog=1/len(self.chunks))
        
        self.update_progress_text("Fully Transcribed")

    def chatgpt(self):
        for i in range(self.results):
            if i == 0:
                self.INSTRUCTION = self.startInstruction
                LaTeXCode = ""
            else:
                self.INSTRUCTION = self.continueInstruction
                LaTeXCode = str(response.choices[0].message.content)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": self.disclaimerInstruction + self.INSTRUCTION + LaTeXCode + str(self.results[i])}],
                stream=False,
            )

            self.update_progress_text(f"Response #{i} retrieved.")

        print(response.choices[0].message.content)

    # Transcribe & Make LaTeX file
    def button_transcribe(self): # Press transcribe button
        # Husk at sæt try statement når færdig
        self.progress = -1
        self.update_progress()
        self.chatkey = self.API_textbox.get()
        self.updateAPIKey(self.chatkey)
        self.saveToFile('API_KEY', self.chatkey)
        if self.file:
            self.update_progress_text(f"File found.")
            time.sleep(0.25)
            if self.chatkey: #Check også om chatgpt api key virker først!!!!!! VIGTIGGGG
                self.update_progress_text(f"API Key found.")
                time.sleep(0.25)
                self.update_progress_text(f"Connecting to OpenAI.")
                self.client = OpenAI()
                if ".mp4" in str(self.file).lower(): # convert kun hvis .mp4
                    self.update_progress_text(f"Converting to .wav (may take a while).")
                    video = VideoFileClip(self.file)
                    video.audio.write_audiofile("temp.wav")
                self.update_progress()
                self.update_progress_text(f"Starting Transcription.")
                self.transcribe()
                self.update_progress()
                self.update_progress_text(f"Connecting to ChatGPT API")
                self.chatgpt()
                self.update_progress()
            else:
                self.update_progress_text(f"Enter API key first.")
        else:
            self.update_progress_text(f"No file selected.")

        
    

app = App()
app.mainloop()
