# rpi-voice-assistant
A Raspberry Pi based voice assistant running on LLM 

![image](img/Rpi_assistant.jpg)

## Preparation

### Hardware
You must have a Python3-enabled system with audio input/output capability. 
The audio capture device must be capable of capturing at 16Khz. 

### System dependencies
This application requires the `PyAudio` package that has system dependencies: 
```bash
sudo apt-get install -y python3 python3-pip python3-all-dev python3-pyaudio portaudio19-dev libsndfile1 mpg123
```

### Python dependencies
Python dependencies can be installed with the following command: 
```bash
pip3 install -r requirements.txt
```

### GCP Account
The RPI voice assistant requires Google Speech-to-text API access.  
Make sure that your user/service account has the correct access permissions.  
Setup instructions can be found on the [official guide](https://cloud.google.com/speech-to-text/docs/libraries).

### App configuration
The Voiceflow API key must be specified as an environment variable `VF_API_KEY`. You can learn more about Voiceflow API keys and how to generate them [here](https://www.voiceflow.com/blog/voiceflow-api).  

To run the application, you must specify the following in the `config.yaml`: 
| Parameter | Purpose |
| --------- | ------- |
| wakewords | A list of `porcupine`-supported wake words that can be used to invoke the system |
| picovice_access_key | The access key for Picovoice's Porcupine engine |
| RATE | The audio sampling rate, e.g., 16000 |
| language_code | The language code for the ASR system, e.g., "en-US" |

## Usage
Run 
```bash
python3 ./src/main.py
```


## wakeup solution
- picovoice
- snowboy
- 亚博MVE01
- https://github.com/wzpan/wukong-robot/issues/285