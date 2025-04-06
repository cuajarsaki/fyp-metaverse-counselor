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
        self.messages = [
            {"role": "system", "content": "以下のルールに従って会話を進めます。"},
            {"role": "system", "content": f"{self.human_name} と {self.ai_name} が会話を始めます。"},
            {"role": "system", "content": "あなたは優秀な心理カウンセラー。3文以下で話し内容は簡潔です。"},
            {"role": "system", "content": "タメ口で喋りますが、非常に優しい友達として喋る。"},
            {"role": "system", "content": "第一人称は「私」。話題を広げることを心かけている。"},
            {"role": "system", "content": "あなたな主な役割は人に癒しを与え、悩みを寄り添うこと"},
            {"role": "system", "content": "あなたの返答は日本語だけ喋る。"},
            {"role": "system", "content": "分からない単語が出たときに、似たような発音する単語「」のことかな？と尋ねる"},
            {"role": "system", "content": "日本語以外の返事が貰ったときに「なにー？もう一回言ってくれると助かる」と返事する"},
            {"role": "system", "content": "いい話し合いできるように、時々質問を投げて、話題を広げる"}
        ]

    def response(self, user_input: str) -> str:

        try:
            self.messages.append({"role": "user", "content": user_input})

            # APIからの応答の取得
            resp = openai.ChatCompletion.create(
                model=self.engine,
                messages=self.messages,
                **self.chat_kwds
            )

            # 応答の抽出と追加
            message = resp["choices"][0]["message"]["content"]
            self.messages.append({"role": "assistant", "content": message})

            # 会話履歴のサイズ管理 (オプション)
            if len(self.messages) > 50:  # 例: 50メッセージを超えた場合
                self.messages = self.messages[-50:]  # 最新の50メッセージのみ保持

            return message

        except Exception as e:
            return f"An unexpected error occurred: {e}"