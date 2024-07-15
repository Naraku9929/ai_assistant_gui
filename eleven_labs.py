from elevenlabs import generate, stream, set_api_key, voices, play, save
from requests.exceptions import HTTPError
import time
import os
from custom_errors import AIAssistantError

class ElevenLabsManager:
    def __init__(self):
        self.api_key = None
        self.voices_list = None

    def initialize(self):
        try:
            self.api_key = os.environ['ELEVENLABS_API_KEY']
            set_api_key(self.api_key)
            # Fetch and store the list of voices
            self.voices_list = voices()
            print(f"\nAll ElevenLabs voices: \n{self.voices_list}\n")
        except KeyError:
            raise AIAssistantError("ELEVENLABS_API_KEY not found in environment variables.")
        except Exception as e:
            raise AIAssistantError(f"Error initializing ElevenLabs: {str(e)}")

    def cleanup(self):
        pass

    def text_to_audio(self, input_text, voice="Rachel", save_as_wave=True, subdirectory=""):
        if not self.api_key:
            self.initialize()

        try:
            audio_saved = generate(
                text=input_text,
                voice=voice,
                model="eleven_monolingual_v1"
            )
        except HTTPError as e:
            print(f"An error occurred: {e.response.json()}")
            raise AIAssistantError(f"ElevenLabs API error: {str(e)}")
        except Exception as e:
            raise AIAssistantError(f"Error in text-to-audio conversion: {str(e)}")

        file_extension = "wav" if save_as_wave else "mp3"
        file_name = f"___Msg{str(hash(input_text))}.{file_extension}"
        tts_file = os.path.join(os.path.abspath(os.curdir), subdirectory, file_name)
        
        try:
            save(audio_saved, tts_file)
            return tts_file
        except Exception as e:
            raise AIAssistantError(f"Error saving audio file: {str(e)}")

    def text_to_audio_played(self, input_text, voice="Rachel"):
        if not self.api_key:
            self.initialize()

        try:
            audio = generate(
                text=input_text,
                voice=voice,
                model="eleven_monolingual_v1"
            )
            play(audio)
        except HTTPError as e:
            print(f"An error occurred: {e.response.json()}")
            raise AIAssistantError(f"ElevenLabs API error: {str(e)}")
        except Exception as e:
            raise AIAssistantError(f"Error in text-to-audio playback: {str(e)}")

    def text_to_audio_streamed(self, input_text, voice="Rachel"):
        if not self.api_key:
            self.initialize()

        try:
            audio_stream = generate(
                text=input_text,
                voice=voice,
                model="eleven_monolingual_v1",
                stream=True
            )
            stream(audio_stream)
        except HTTPError as e:
            print(f"An error occurred: {e.response.json()}")
            raise AIAssistantError(f"ElevenLabs API error: {str(e)}")
        except Exception as e:
            raise AIAssistantError(f"Error in text-to-audio streaming: {str(e)}")

    def get_available_voices(self):
        if not self.voices_list:
            self.initialize()
        return self.voices_list