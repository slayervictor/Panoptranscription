import customtkinter as ctk
from tkinter import filedialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.file = ""

        self.title("Panoptranscription")
        self.geometry("500x700")
        self.grid_columnconfigure((0, 1), weight=1)
        
        self.translation_check = ctk.CTkCheckBox(self, text="Translate to English? (not necessary if already English)")
        self.translation_check.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
        
        self.select_file_button = ctk.CTkButton(self, text="Choose File", command=self.choose_file)
        self.select_file_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.file_entry = ctk.CTkEntry(self, width=400)
        self.file_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        self.button = ctk.CTkButton(self, text="Transcribe", command=self.button_transcribe)
        self.button.grid(row=2, column=0, padx=20, pady=10, sticky="ew", columnspan=2)
        
    def choose_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Mp4 or Mp3 Files", "*.mp4;*.mp3"), ("All Files", "*.*")])
        if file_selected:
            self.file = file_selected
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, self.file)

    def button_transcribe(self): 
        if self.file:
            print(f"Transcribing: {self.file}")
        else:
            print("No file selected!")

app = App()
app.mainloop()
