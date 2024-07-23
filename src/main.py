import os
import time
import struct
import sys
import yaml
import pvporcupine
import logging

import audio
from ASRClient import MicrosoftASRClient  # Updated import
from LLMClient import LLMClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_file="config.yaml"):
    logger.info("Loading configuration from %s", config_file)
    with open(config_file) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        return yaml.load(file, Loader=yaml.FullLoader)

def main():
    logger.info("Starting main function")
    # Set the environment variable for Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-file.json"
    
    config = load_config()

    RATE = config["RATE"]
    language_code = config["language_code"]
    access_key = config["picovice_access_key"]
    wakewords = config["wakewords"]
    subscription_key = config["microsoft_tts"]["subscription_key"]
    region = config["microsoft_tts"]["region"]

    # Wakeword setup
    porcupine = pvporcupine.create(access_key=access_key, keywords=wakewords)
    CHUNK = porcupine.frame_length  # 512 entries

    # ASR setup
    asr_client = MicrosoftASRClient(language_code, subscription_key, region)  # Updated initialization
    asr_client.tts("Starting voice assistant! Listening for wakewords: " + ", ".join(wakewords))

    # LLM setup
    llm_client = LLMClient(api_key=os.getenv('OPENAI_API_KEY', "sk-"), base_url="https://openai.pjq.me/v1/")

    with audio.MicrophoneStream(RATE, CHUNK) as stream:
        logger.info("Starting voice assistant!")
        while True:
            pcm = stream.get_sync_frame()
            if len(pcm) == 0:
                # Protects against empty frames
                continue
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                logger.info("Wakeword Detected")
                audio.beep()

                import random

                responses = [
                    "Hello!",
                    "Ready.",
                    "Go ahead.",
                    "Hi!",
                    "Yes?"
                ]
                asr_client.tts(random.choice(responses))
                
                end = False
                last_interaction_time = time.time()
                while not end:
                    stream.start_buf()  # Only start the stream buffer when we detect the wakeword
                    logger.info("Starting transcription process")
                    recognizdText = asr_client.transcribe()  # Updated method call
                    logger.info("Transcription result: %s", recognizdText)
                    stream.stop_buf()

                    # Check for stop command
                    if recognizdText.lower() in ["stop", "exit", "quit"]:
                        end = True
                        logger.info("Stopping voice assistant")
                        asr_client.tts("Goodbye!")
                        break

                    # Check for None or empty utterance
                    if recognizdText is None or recognizdText.strip() == "":
                        logger.warning("Received empty or None recognizdText, skipping interaction")
                    else:
                        # Send request to LLM service and get response
                        response_message = llm_client.interact(recognizdText)
                        
                        logger.info("Response: " + response_message)
                        if response_message is not None:
                            asr_client.tts(response_message)
                            # Update last interaction time
                            last_interaction_time = time.time()
                        audio.beep()


                    # Check for inactivity timeout
                    if time.time() - last_interaction_time > 10:
                        logger.info("No interaction for 10 seconds, going back to sleep")
                        asr_client.tts("Going back to sleep")
                        end = True

if __name__ == "__main__":
    main()