from typing import Optional
import whisper
import torch

class SpeechRecongition:
    def __init__(
        self,
        model_name: str = "large-v3",
        device: str = "cuda",
        options: Optional[whisper.DecodingOptions] = whisper.DecodingOptions(language="Japanese"),
    ) -> None:

        self.model = whisper.load_model(model_name, device=device)
        self.options = options

    def recongnize(self, audio: torch.Tensor) -> tuple[list[dict], str]:

        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        _, probs = self.model.detect_language(mel)
        result = whisper.decode(self.model, mel, self.options)

        return probs, result.text
