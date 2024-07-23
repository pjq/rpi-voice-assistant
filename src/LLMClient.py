import openai

class LLMClient:
    def __init__(self, api_key, model="gpt-3.5-turbo", base_url="https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        openai.api_key = self.api_key
        openai.api_base = self.base_url

    def interact(self, utterance):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": utterance},
            ],
        )
        message = response.choices[0].message['content']
        return message
