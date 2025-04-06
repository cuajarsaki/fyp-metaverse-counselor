from typing import Any
import openai

class ChatBot:
    """Interface class for chatbot using GPT-4."""

    def __init__(
        self,
        api_key_file_path: Any,
        engine: str = "gpt-4",
        max_tokens=128,
        temperature=0.9,
        human_name: str = "人間:",
        ai_name: str = "人工知能:",
        **kwds: dict,
    ) -> None:
        """
        Args:
            api_key_file_path (str | Pathlike): Path to the api key file.
            engine (str): OpenAI language model engine name.
            max_tokens (int): The maximum number of tokens to generate in the completion.
            temperature (float): Temperature of output probability.
            kwds: Other key word arguments for `ChatCompletion.create`.
        """

        with open(api_key_file_path, "r", encoding="utf-8") as f:
            api_key = f.read()
        if api_key == "":
            raise RuntimeError(f"Please write api key to {api_key_file_path}")

        openai.api_key = api_key
        self.engine = engine
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.human_name = human_name
        self.ai_name = ai_name
        self.chat_kwds = kwds
        self.reset()

    def reset(self):
        """Reset the chat session."""
        self.chat_session = None

    def response(self, user_input: str) -> str:
        """Communicate to OpenAI API using GPT-4.

        Args:
            user_input (str): User input text.

        Returns:
            response (str): Response text.
        """

        if self.chat_session is None:
            self.chat_session = openai.ChatCompletion.create(
                model=self.engine,
                messages=[{"role": "system", "content": f"{self.human_name} がチャットを始めました。"}],
                **self.chat_kwds
            )

        resp = openai.ChatCompletion.create(
            model=self.engine,
             messages=[
                {"role": "system", "content": "You are a helpful psychological counselor.your reply is concise.Not more than 3 sentences.タメ口で優しい友達として喋る、第一人称は「私」、内容は具体的です"},
                {"role": "user", "content": user_input}],
            #session_id=self.chat_session["id"],
            **self.chat_kwds
        )

        message = resp["choices"][0]["message"]["content"]
        return message
