from openai import OpenAI
import tiktoken
import os
from rich import print
from custom_errors import AIAssistantError

def num_tokens_from_messages(messages, model='gpt-4'):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    except Exception:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

class OpenAiManager:
    def __init__(self):
        self.chat_history = []  # Stores the entire conversation
        self.client = None

    def initialize(self):
        try:
            self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except KeyError:
            raise Exception("OPENAI_API_KEY not found in environment variables.")

    def cleanup(self):
        pass

    def chat(self, prompt=""):
        if not self.client:
            self.initialize()

        if not prompt:
            print("Didn't receive input!")
            return

        # Check that the prompt is under the token context limit
        chat_question = [{"role": "user", "content": prompt}]
        if num_tokens_from_messages(chat_question) > 8000:
            print("The length of this chat question is too large for the GPT model")
            return

        print("[yellow]\nAsking ChatGPT a question...")
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=chat_question
            )

            # Process the answer
            openai_answer = completion.choices[0].message.content
            print(f"[green]\n{openai_answer}\n")
            return openai_answer
        except Exception as e:
            raise Exception(f"Error in OpenAI API call: {str(e)}")

    def chat_with_history(self, prompt=""):
        if not self.client:
            self.initialize()

        if not prompt:
            print("Didn't receive input!")
            return

        # Add our prompt into the chat history
        self.chat_history.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(f"[coral]Chat History has a current token length of {num_tokens_from_messages(self.chat_history)}")
        while num_tokens_from_messages(self.chat_history) > 8000:
            self.chat_history.pop(1)  # We skip the 1st message since it's the system message
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history)}")

        print("[yellow]\nAsking ChatGPT a question...")
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.chat_history
            )

            # Add this answer to our chat history
            self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

            # Process the answer
            openai_answer = completion.choices[0].message.content
            print(f"[green]\n{openai_answer}\n")
            return openai_answer
        except Exception as e:
            raise Exception(f"Error in OpenAI API call: {str(e)}")