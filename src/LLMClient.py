import openai
class LLMClient:
    def __init__(self, api_key, model="gpt-4o", base_url="https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.messages = [
            {"role": "system", "content": "You are a helpful voice assistant, Jarvis, keep the response friendly for tts."}
        ]
        openai.api_key = self.api_key
        openai.base_url = self.base_url

    def interact(self, utterance):
        self.messages.append({"role": "user", "content": utterance})
        completion = openai.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        message = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": message})
        
        # Keep only the last 10 messages
        if len(self.messages) > 11:  # 10 user/assistant messages + 1 system message
            self.messages = self.messages[-11:]
        
        return message