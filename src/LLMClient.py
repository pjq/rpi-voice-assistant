from voiceflow import Voiceflow

class LLMClient:
    def __init__(self, api_key, version_id):
        self.client = Voiceflow(api_key, version_id)

    def state_uninitialized(self):
        return self.client.state_uninitialized()

    def init_state(self):
        return self.client.init_state()

    def interact(self, utterance):
        return self.client.interact(utterance)

    def clear_state(self):
        self.client.clear_state()