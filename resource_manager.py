from contextlib import contextmanager
from openai_chat import OpenAiManager
from azure_speech_to_text import SpeechToTextManager
from eleven_labs import ElevenLabsManager
from audio_player import AudioManager
from custom_errors import AIAssistantError

class ResourceManager:
    def __init__(self):
        self.speech_to_text = None
        self.openai = None
        self.eleven_labs = None
        self.audio = None

    def initialize(self):
        try:
            from azure_speech_to_text import SpeechToTextManager
            from openai_chat import OpenAiManager
            from eleven_labs import ElevenLabsManager
            from audio_player import AudioManager

            self.speech_to_text = SpeechToTextManager()
            self.speech_to_text.initialize()

            self.openai = OpenAiManager()
            self.openai.initialize()

            self.eleven_labs = ElevenLabsManager()
            self.eleven_labs.initialize()

            self.audio = AudioManager()
            self.audio.initialize()
        except Exception as e:
            raise AIAssistantError(f"Error initializing resources: {str(e)}")

    def cleanup(self):
        for resource in [self.speech_to_text, self.openai, self.eleven_labs, self.audio]:
            if resource:
                try:
                    resource.cleanup()
                except Exception as e:
                    print(f"Error during cleanup of {resource.__class__.__name__}: {str(e)}")

    def handle_error(self, error):
        if isinstance(error, AIAssistantError):
            print(f"AI Assistant Error: {str(error)}")
        elif isinstance(error, Exception):
            print(f"Unexpected error: {str(error)}")
        else:
            print(f"Unknown error type: {str(error)}")

@contextmanager
def ResourceContext():
    manager = ResourceManager()
    try:
        manager.initialize()
        yield manager
    except Exception as e:
        manager.handle_error(e)
    finally:
        manager.cleanup()