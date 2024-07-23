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
    llm_client = LLMClient(os.getenv('LLM_API_KEY', "dummy_key"), config["llm_VersionID"])

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
                    if llm_client.state_uninitialized(): 
                        # First session
                        print("Initializing first session")
                        response = llm_client.init_state()
                    else:
                        stream.start_buf()  # Only start the stream buffer when we detect the wakeword
                        audio_generator = stream.generator()
                        utterance = asr_client.transcribe(audio_generator)
                        stream.stop_buf()

                        # Send request to LLM service and get response
                        response = llm_client.interact(utterance)
                    
                    for item in response["trace"]:
                        if item["type"] == "speak":
                            payload = item["payload"]
                            message = payload["message"]
                            print("Response: " + message)
                            audio.play(payload["src"])
                        elif item["type"] == "end":
                            print("-----END-----")
                            llm_client.clear_state()
                            end = True
                            audio.beep()

if __name__ == "__main__":
    main()