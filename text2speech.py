import os
from dotenv import load_dotenv
from pathlib import Path
from deepgram import DeepgramClient

import platform
import subprocess


# 1. load api_key
load_dotenv()

def save_text2speech_file(text : str, save_filepath : Path):
    # 2. create client
    client = DeepgramClient(api_key = os.getenv("DEEPGRAM_API_KEY"))

    model = client.speak.v1.audio.generate(model = "aura-2-thalia-en", text = text, encoding = "mp3")

    # save audio
    with save_filepath.open("wb") as file: 
        for chunk in model:
            file.write(chunk)

    return save_filepath  



# play audio
def play_audio(save_filepath):

    if platform.system == "Darwin":   # i.e. macOS
        subprocess.run(["afplay", str(save_filepath)])

    elif platform.system == "Linux":
        subprocess.run(["xdg-open", str(save_filepath)])

    else: # Windows
        os.startfile(save_filepath)
