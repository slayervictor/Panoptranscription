import customtkinter as ctk
from tkinter import filedialog
from openai import OpenAI
from moviepy import VideoFileClip, audio
import os
import time
import json


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
        self.progressbar.grid(row=4, column=0, padx=20, pady=10, sticky="ew", columnspan=2)
        self.progressbar.set(self.progress)  # Set initial value (0 to 1)
        
        self.progresstext = ""
        self.label = ctk.CTkLabel(self, text=self.progresstext, font=("Consolas", 16))
        self.label.grid(row=5, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

        self.API_textbox = ctk.CTkEntry(self)
        self.API_textbox.grid(row=1, column=1, padx=0, pady=20, columnspan=2,sticky="ew")
        try:
            self.chatkey = str(self.data["API_KEY"])
            self.API_textbox.insert("end",self.chatkey)
        except:
            pass

        self.labelAPI = ctk.CTkLabel(self, text="ChatGPT API Key:", font=("Consolas", 16))
        self.labelAPI.grid(row=1, column=0, padx=5, pady=20,sticky="ew")

        # Elements
        self.translation_check = ctk.CTkCheckBox(self, text="Translate to English? (not necessary if already English)")
        self.translation_check.grid(row=2, column=1, padx=20, pady=20, sticky="ew")
        
        self.select_file_button = ctk.CTkButton(self, text="Choose File", command=self.choose_file)
        self.select_file_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.file_entry = ctk.CTkEntry(self, width=400)
        self.file_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        try:
            self.file = str(self.data["FILE"])
            self.file_entry.insert("end",str(self.data["FILE"]))
        except:
            pass

        self.button = ctk.CTkButton(self, text="Transcribe", command=self.button_transcribe)
        self.button.grid(row=3, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

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
    def update_progress(self):
        self.progress += 1
        self.progressbar.set(self.progress/2)  # Update progress bar
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

    def transcribe(self):
        audio_file = open("temp.wav", "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )

        print(transcription.text)

    # Transcribe
    def button_transcribe(self): # Press transcribe button
        try:
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
                        video.audio.write_audiofile("temp.wav", codec='pcm_s16le')
                    self.update_progress()
                    self.update_progress_text(f"Starting Transcription.")
                    self.transcribe()
                    self.update_progress()
                    self.update_progress_text(f"Done.")
                else:
                    self.update_progress_text(f"Enter API key first.")
            else:
                self.update_progress_text(f"No file selected.")
        except:
            self.update_progress_text(f"Something went wrong! Check if the file is correct and the API key is valid.")
        
    

app = App()
app.mainloop()
