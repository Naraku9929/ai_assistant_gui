import time
import azure.cognitiveservices.speech as speechsdk
import keyboard
import os
from custom_errors import AIAssistantError

class SpeechToTextManager:
    def __init__(self):
        self.azure_speechconfig = None
        self.azure_audioconfig = None
        self.azure_speechrecognizer = None

    def initialize(self):
        try:
            self.azure_speechconfig = speechsdk.SpeechConfig(
                subscription=os.environ['AZURE_TTS_KEY'],
                region=os.environ['AZURE_TTS_REGION']
            )
            self.azure_speechconfig.speech_recognition_language = "en-US"
        except KeyError as e:
            raise AIAssistantError(f"Missing environment variable: {str(e)}")
        except Exception as e:
            raise AIAssistantError(f"Error initializing Azure Speech SDK: {str(e)}")

    def cleanup(self):
        pass

    def _ensure_initialized(self):
        if not self.azure_speechconfig:
            self.initialize()

    def speechtotext_from_mic(self):
        self._ensure_initialized()
        self.azure_audioconfig = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speechconfig, audio_config=self.azure_audioconfig)

        print("Speak into your microphone.")
        try:
            speech_recognition_result = self.azure_speechrecognizer.recognize_once_async().get()
            text_result = speech_recognition_result.text

            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print("Recognized: {}".format(speech_recognition_result.text))
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))

            print(f"We got the following text: {text_result}")
            return text_result
        except Exception as e:
            raise AIAssistantError(f"Error in speech-to-text conversion: {str(e)}")

    def speechtotext_from_file(self, filename):
        self._ensure_initialized()
        self.azure_audioconfig = speechsdk.AudioConfig(filename=filename)
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speechconfig, audio_config=self.azure_audioconfig)

        print("Listening to the file \n")
        try:
            speech_recognition_result = self.azure_speechrecognizer.recognize_once_async().get()

            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print("Recognized: \n {}".format(speech_recognition_result.text))
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))

            return speech_recognition_result.text
        except Exception as e:
            raise AIAssistantError(f"Error in speech-to-text conversion from file: {str(e)}")

    def speechtotext_from_file_continuous(self, filename):
        self._ensure_initialized()
        self.azure_audioconfig = speechsdk.audio.AudioConfig(filename=filename)
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speechconfig, audio_config=self.azure_audioconfig)

        done = False
        def stop_cb(evt):
            print('CLOSING on {}'.format(evt))
            nonlocal done
            done = True

        all_results = []
        def handle_final_result(evt):
            all_results.append(evt.result.text)

        self.azure_speechrecognizer.recognized.connect(handle_final_result)
        self.azure_speechrecognizer.session_stopped.connect(stop_cb)
        self.azure_speechrecognizer.canceled.connect(stop_cb)

        print("Now processing the audio file...")
        self.azure_speechrecognizer.start_continuous_recognition()
        
        try:
            while not done:
                time.sleep(.5)
        finally:
            self.azure_speechrecognizer.stop_continuous_recognition()

        final_result = " ".join(all_results).strip()
        print(f"\n\nHere's the result we got from continuous file read!\n\n{final_result}\n\n")
        return final_result

    def speechtotext_from_mic_continuous(self, stop_key='p'):
        self._ensure_initialized()
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speechconfig)

        done = False
        all_results = []

        def recognized_cb(evt):
            print('RECOGNIZED: {}'.format(evt))
            all_results.append(evt.result.text)

        def stop_cb(evt):
            print('CLOSING speech recognition on {}'.format(evt))
            nonlocal done
            done = True

        self.azure_speechrecognizer.recognized.connect(recognized_cb)
        self.azure_speechrecognizer.session_stopped.connect(stop_cb)
        self.azure_speechrecognizer.canceled.connect(stop_cb)

        result_future = self.azure_speechrecognizer.start_continuous_recognition_async()
        result_future.get()  # wait for initialization to complete
        print('Continuous Speech Recognition is now running, say something.')

        try:
            while not done:
                if keyboard.read_key() == stop_key:
                    print("\nEnding azure speech recognition\n")
                    self.azure_speechrecognizer.stop_continuous_recognition_async()
                    break
        except Exception as e:
            raise AIAssistantError(f"Error in continuous speech-to-text conversion: {str(e)}")
        finally:
            final_result = " ".join(all_results).strip()
            print(f"\n\nHere's the result we got!\n\n{final_result}\n\n")
            return final_result
