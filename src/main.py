import os
import time
import struct
import sys
import yaml
import pvporcupine

import audio
import ASRClient  # Abstracted ASR client
import LLMClient  # Abstracted LLM client

RATE = 16000
language_code = "en-US"  # a BCP-47 language tag

def load_config(config_file="config.yaml"):
    with open(config_file) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        return yaml.load(file, Loader=yaml.FullLoader)


def main():
    config = load_config()

    # Wakeword setup
    porcupine = pvporcupine.create(keywords=config["wakewords"])
    CHUNK = porcupine.frame_length  # 512 entries

    # ASR setup
    asr_client = ASRClient(language_code, RATE)

    # LLM setup
    llm_client = LLMClient(api_key=os.getenv('OPENAI_API_KEY', "sk-"), base_url="https://sapai.pjq.me/v1")

    with audio.MicrophoneStream(RATE, CHUNK) as stream:
        print("Starting voice assistant!")
        while True:
            pcm = stream.get_sync_frame()
            if len(pcm) == 0:
                # Protects against empty frames
                continue
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("Wakeword Detected")
                audio.beep()
                end = False
                while not end:
                    stream.start_buf()  # Only start the stream buffer when we detect the wakeword
                    audio_generator = stream.generator()
                    utterance = asr_client.transcribe(audio_generator)
                    stream.stop_buf()

                    # Send request to LLM service and get response
                    response_message = llm_client.interact(utterance)
                    
                    print("Response: " + response_message)
                    # Assuming audio.play can handle text-to-speech conversion
                    audio.play(response_message)
                    end = True
                    audio.beep()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()