import logging
from google.cloud import speech_v1 as speech
import audio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


import azure.cognitiveservices.speech as speechsdk

class MicrosoftASRClient:
    def __init__(self, language_code, subscription_key, region):
        self.speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
        self.speech_config.speech_recognition_language = language_code
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=speechsdk.audio.AudioOutputConfig(use_default_speaker=True))

    def transcribe(self):
        speech_recognition_result = self.speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info("Recognized text: %s", speech_recognition_result.text)
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            logger.info("No speech could be recognized: %s", speech_recognition_result.no_match_details)
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            logger.warning("Speech Recognition canceled: %s", cancellation_details.reason)
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error("Error details: %s", cancellation_details.error_details)
                logger.error("Did you set the speech resource key and region values?")
        return ""

    def tts(self, text):
        self.speech_config.speech_synthesis_voice_name = 'zh-CN-XiaoxuanNeural'
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logger.warning("Speech synthesis canceled: %s", cancellation_details.reason)
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    logger.error("Error details: %s", cancellation_details.error_details)
                    logger.error("Did you set the speech resource key and region values?")