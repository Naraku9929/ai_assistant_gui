import time
import keyboard
import json
from rich import print
from resource_manager import ResourceManager, ResourceContext, AIAssistantError

ELEVENLABS_VOICE = "Aaryan"  # Replace this with the name of whatever voice you have created on Elevenlabs
BACKUP_FILE = "ChatHistoryBackup.txt"
CONFIG_FILE = "ai_assistant_config.json"

def load_ai_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print("AI assistant configuration loaded from file.")
        return config
    except FileNotFoundError:
        print("[yellow]No custom configuration found. Using default settings.[/yellow]")
        return None
    except json.JSONDecodeError:
        print("[red]Error decoding the configuration file. Using default settings.[/red]")
        return None

def update_system_message(config, openai_manager):
    if config is None:
        return

    custom_text = config.get('custom_text', '')

    new_system_message = {
        "role": "system",
        "content": custom_text
    }

    if openai_manager.chat_history and openai_manager.chat_history[0]['role'] == 'system':
        openai_manager.chat_history[0] = new_system_message
    else:
        openai_manager.chat_history.insert(0, new_system_message)

def main_loop(resource_manager):
    print("[green]AI Assistant is running. Press F4 to start an interaction, or press Ctrl+C to exit.[/green]")
    try:
        while True:
            if keyboard.read_key() != "f4":
                time.sleep(0.1)
                continue

            print("[green]User pressed F4 key! Now listening to your microphone:[/green]")

            try:
                # Load the latest AI configuration
                config = load_ai_config()
                update_system_message(config, resource_manager.openai)

                # Get question from mic
                mic_result = resource_manager.speech_to_text.speechtotext_from_mic_continuous()
                
                # Send question to OpenAI
                openai_result = resource_manager.openai.chat_with_history(mic_result)
                
                # Write the results to txt file as a backup
                with open(BACKUP_FILE, "w") as file:
                    json.dump(resource_manager.openai.chat_history, file, indent=2)

                # Mark the ChatGPT response for easy identification
                print(f"CHATGPT_RESPONSE_START\n{openai_result}\nCHATGPT_RESPONSE_END")

                # Send it to ElevenLabs to turn into cool audio
                elevenlabs_output = resource_manager.eleven_labs.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

                # Play the mp3 file
                resource_manager.audio.play_audio(elevenlabs_output, True, True, True)

                print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")

            except AIAssistantError as e:
                print(f"[red]An error occurred: {str(e)}[/red]")
                print("[yellow]The AI Assistant will continue running. Press F4 to try again.[/yellow]")

    except KeyboardInterrupt:
        print("[yellow]AI Assistant stopping...[/yellow]")

if __name__ == "__main__":
    with ResourceContext() as resource_manager:
        try:
            main_loop(resource_manager)
        except Exception as e:
            print(f"[red]A critical error occurred: {str(e)}[/red]")
            print("[red]The AI Assistant will now exit.[/red]")