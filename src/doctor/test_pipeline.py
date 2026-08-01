from src.doctor.components.brain import doctor
from src.doctor.components.speech2text import record_audio, transcribe_patient_voice
from src.doctor.components.text2speech import save_text2speech_file, play_audio
from pathlib import Path


def pipeline(audio_filepath, image_filepath, video_filepath):

    record_audio(audio_filepath)

    patient_transcribed = transcribe_patient_voice(audio_filepath)

    doctor_text_response = doctor(patient_query = patient_transcribed, image_filepath = image_filepath, video_filepath = video_filepath)

    doctor_audio_response = save_text2speech_file(text = doctor_text_response, save_filepath = Path("doctor_audio_response.mp3"))

    play_audio(Path("doctor_audio_response.mp3"))

if __name__ == "__main__":
    pipeline(audio_filepath="patient_query_audio.mp3", image_filepath = "samples/test-image.jpeg", video_filepath = "samples/test-video.mp4")
