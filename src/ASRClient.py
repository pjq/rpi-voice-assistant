from google.cloud import speech_v1 as speech
import audio


class ASRClient:
    def __init__(self, language_code, rate):
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=rate,
            language_code=language_code,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config, interim_results=True
        )

    def transcribe(self, audio_generator):
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = self.client.streaming_recognize(self.streaming_config, requests)
        return audio.process(responses)