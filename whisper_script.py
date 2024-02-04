from transformers import pipeline
def audio_transcription(audio_path):
    whisper = pipeline("automatic-speech-recognition",
                       "openai/whisper-tiny.en", 
                       device = "cuda:0")
    transcription = whisper(audio_path)
    return transcription['text']
