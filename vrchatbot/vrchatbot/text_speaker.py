import requests
import json
import numpy as np
import soundcard as sc
from typing import Optional, Union

class TextSpeaker:
    """Text speaker using VOICEVOX."""

    def __init__(self, speaker_index_or_name: Optional[Union[str, int]] = None) -> None:
        """Initializes the TextSpeaker with VOICEVOX.

        Args:
            speaker_index_or_name (Optional[Union[str, int]]): The name or index of the audio output device.
        """
        self.speaker_index_or_name = speaker_index_or_name

    def speak_text(self, text: str) -> None:
        """Converts text to speech using VOICEVOX.

        Args:
            text (str): Japanese text.
        """
        audio_query_response = self.post_audio_query(text)
        wav_file = self.post_synthesis(audio_query_response)
        self.play_wavfile(wav_file)

    def post_audio_query(self, text: str, speed_scale: float = 1.4) -> dict:
        query_params = {'text': text, 'speaker':1 }
        response = requests.post('http://127.0.0.1:50021/audio_query', params=query_params)
        query = response.json()
        query['speedScale'] = speed_scale
        return query

    def post_synthesis(self, audio_query_response: dict) -> bytes:
        params = {'speaker': 54}
        headers = {'content-type': 'application/json'}
        audio_query_response_json = json.dumps(audio_query_response)
        res = requests.post(
            'http://127.0.0.1:50021/synthesis',
            data=audio_query_response_json,
            params=params,
            headers=headers
        )
        return res.content

    def play_wavfile(self, wav_file: bytes):
        """Plays the given WAV file on the specified audio device using soundcard."""

        # Convert bytes data to numpy array
        wave_data = np.frombuffer(wav_file, dtype=np.int16)

        # Select the speaker
        speaker = self.select_speaker()

        # Play the audio
        speaker.play(wave_data / np.iinfo(np.int16).max, samplerate=24000)

    def select_speaker(self):
        """Selects the speaker based on the given index or name."""
        if isinstance(self.speaker_index_or_name, str):
            try:
                return sc.get_speaker(self.speaker_index_or_name)
            except ValueError:
                raise RuntimeError(f"Audio device '{self.speaker_index_or_name}' not found")
        elif isinstance(self.speaker_index_or_name, int):
            speakers = sc.all_speakers()
            if 0 <= self.speaker_index_or_name < len(speakers):
                return speakers[self.speaker_index_or_name]
            else:
                raise RuntimeError(f"Audio device index {self.speaker_index_or_name} is out of range")
        else:
            return sc.default_speaker()
