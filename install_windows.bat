@echo off

:: Install FFmpeg (Essentials Build) using winget
winget install "FFmpeg (Essentials Build)"

:: Check if Python is installed, and install packages from requirements.txt if available
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pause
