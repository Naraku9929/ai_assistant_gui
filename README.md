AI Assistant Personality Manager
This project is an AI Assistant Personality Manager that uses OpenAI's GPT model, ElevenLabs for text-to-speech, and Azure Speech-to-Text for voice input. It features a GUI for managing the AI's personality traits and a system for processing voice input, generating responses, and outputting audio.
Features

GUI for managing AI personality traits
Voice input processing using Azure Speech-to-Text
Text generation using OpenAI's GPT model
Text-to-speech conversion using ElevenLabs
Audio playback using Pygame

Components

ai_assistant_gui.py: The main GUI application for managing the AI assistant.
app.py: The core logic for processing input, generating responses, and managing audio output.
eleven_labs.py: Handles interaction with the ElevenLabs API for text-to-speech conversion.
audio_player.py: Manages audio playback using Pygame.
azure_speech_to_text.py: Handles speech-to-text conversion using Azure's services.
openai_chat.py: Manages interaction with OpenAI's GPT model.

Installation

Clone this repository:
git clone https://github.com/your-username/ai_assistant_gui.git
cd ai-assistant-personality-manager

Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the required packages:
pip install -r requirements.txt

Set up environment variables:

OPENAI_API_KEY: Your OpenAI API key
ELEVENLABS_API_KEY: Your ElevenLabs API key
AZURE_SPEECH_KEY: Your Azure Speech Services key
AZURE_SPEECH_REGION: Your Azure Speech Services region



Usage

Start the GUI application:
python ai_assistant_gui.py

Use the sliders in the GUI to adjust the AI's personality traits.
Click "Update AI Assistant" to apply the changes.
Click "Start AI Assistant" to begin the interaction.
Press 'F4' to start speech recognition, then speak your question or command.
Press 'P' to send the captured audio to the AI for processing.
The AI's response will be displayed in the GUI and played back as audio.

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
License
This project is licensed under the MIT License - see the LICENSE file for details.
