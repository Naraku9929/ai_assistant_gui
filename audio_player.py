import pygame
import time
import os
import asyncio
import soundfile as sf
from mutagen.mp3 import MP3
from custom_errors import AIAssistantError

class AudioManager:
    def __init__(self):
        self.mixer = None

    def initialize(self):
        try:
            # Use higher frequency to prevent audio glitching noises
            # Use higher buffer because why not (default is 512)
            pygame.mixer.init(frequency=48000, buffer=1024)
            self.mixer = pygame.mixer
        except pygame.error as e:
            raise AIAssistantError(f"Failed to initialize pygame mixer: {str(e)}")

    def cleanup(self):
        if self.mixer:
            self.mixer.quit()

    def _ensure_initialized(self):
        if not self.mixer:
            self.initialize()

    def play_audio(self, file_path, sleep_during_playback=True, delete_file=False, play_using_music=True):
        self._ensure_initialized()
        
        try:
            print(f"Playing file with pygame: {file_path}")
            
            if play_using_music:
                # Pygame Music can only play one file at a time
                self.mixer.music.load(file_path)
                self.mixer.music.play()
            else:
                # Pygame Sound lets you play multiple sounds simultaneously
                pygame_sound = self.mixer.Sound(file_path) 
                pygame_sound.play()

            if sleep_during_playback:
                # Calculate length of the file, based on the file format
                _, ext = os.path.splitext(file_path)
                if ext.lower() == '.wav':
                    with sf.SoundFile(file_path) as wav_file:
                        file_length = wav_file.frames / wav_file.samplerate
                elif ext.lower() == '.mp3':
                    mp3_file = MP3(file_path)
                    file_length = mp3_file.info.length
                else:
                    raise AIAssistantError("Cannot play audio, unknown file type")

                # Sleep until file is done playing
                time.sleep(file_length)

                # Delete the file
                if delete_file:
                    # Stop Pygame so file can be deleted
                    self.mixer.music.stop()
                    self.mixer.quit()
                    try:  
                        os.remove(file_path)
                        print(f"Deleted the audio file.")
                    except PermissionError:
                        print(f"Couldn't remove {file_path} because it is being used by another process.")
                    except OSError as e:
                        raise AIAssistantError(f"Error deleting audio file: {str(e)}")
                    finally:
                        # Reinitialize mixer after deletion attempt
                        self.initialize()

        except Exception as e:
            raise AIAssistantError(f"Error playing audio: {str(e)}")

    async def play_audio_async(self, file_path):
        self._ensure_initialized()
        
        try:
            print(f"Playing file asynchronously with pygame: {file_path}")
            pygame_sound = self.mixer.Sound(file_path) 
            pygame_sound.play()

            # Calculate length of the file, based on the file format
            _, ext = os.path.splitext(file_path)
            if ext.lower() == '.wav':
                with sf.SoundFile(file_path) as wav_file:
                    file_length = wav_file.frames / wav_file.samplerate
            elif ext.lower() == '.mp3':
                mp3_file = MP3(file_path)
                file_length = mp3_file.info.length
            else:
                raise AIAssistantError("Cannot play audio, unknown file type")

            # We must use asyncio.sleep() here because the normal time.sleep() will block the thread, even if it's in an async function
            await asyncio.sleep(file_length)

        except Exception as e:
            raise AIAssistantError(f"Error playing audio asynchronously: {str(e)}")
