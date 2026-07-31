import speech_recognition as sr   # Provides access to: Microphone, Audio recording, Speech recognition APIs
from pydub import AudioSegment    # Used to: Read audio files, Convert formats, Export audio. Here it converts WAV → MP3.
from io import BytesIO            # Creates an in-memory file instead of writing a temporary WAV file.
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def record_audio(file_path, timeout = 20, phrase_time_limit = None):
    """
    Simplified function to record audio from the microphone and save it as an MP3 file.

    Args:
    file_path (str): Path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_lfimit (int): Maximum time for the phrase to be recorded (in seconds).
    """

    recognizer = sr.Recognizer()

    with sr.Microphone() as source : 
        logging.info("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration = 1)  # For 1 second it listens to background sounds: 
                                                                   # Fan noise, AC noise, Keyboard noise and calculates a noise threshold.
        logging.info("Start speaking now...")

        # Record the audio
        audio_data = recognizer.listen( source,                                   # returns AudioData object
                                        timeout = timeout,
                                        phrase_time_limit = phrase_time_limit
                                        )
        logging.info("Recording complete.")

        # Convert the recorded audio to an MP3 file
        wav_data = audio_data.get_wav_data()                                  # Convert Recording to WAV Byte. Produces - "bytes" containing WAV audio.

        audio_segment = AudioSegment.from_wav( BytesIO(wav_data) )            # Load WAV Into Pydub. Converts: WAV bytes -> AudioSegment, which is easier to manipulate.

        audio_segment.export( file_path,                                      # Export as MP3
                              format="mp3",
                              bitrate="128k"
                            )
        logging.info(f"Audio saved to {file_path}")



import os
# from google import genai   # google sdk doesn't directly support whisper-style endpoint for speech to text. Whereas groq and openai does.
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def transcribe_patient_voice(audio_filepath):

    groq_api_key = os.environ.get("GROQ_API_KEY")

    client = Groq(api_key = groq_api_key)

    with open(audio_filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(file = audio_file, model = os.environ.get("WHISPER_MODEL", "whisper-large-v3-turbo"))

    return transcription.text


        