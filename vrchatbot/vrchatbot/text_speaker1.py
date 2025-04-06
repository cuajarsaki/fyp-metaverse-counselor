import requests
import json
import io
import wave
import pyaudio
from time import sleep
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
        query_params = {'text': text, 'speaker': 1}
        response = requests.post('http://127.0.0.1:50021/audio_query', params=query_params)
        query = response.json()
        query['speedScale'] = speed_scale
        return query

    def post_synthesis(self, audio_query_response: dict) -> bytes:
        params = {'speaker': 1}
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
        """Plays the given WAV file on the specified audio device."""

        # Device index/name handling
        if isinstance(self.speaker_index_or_name, int):
            device_index = self.speaker_index_or_name
        elif isinstance(self.speaker_index_or_name, str):
            device_index = self.get_device_index(self.speaker_index_or_name)
            if device_index is None:
                raise RuntimeError(f"Audio device '{self.speaker_index_or_name}' not found")
        else:
            device_index = None  # Use default device

        wr: wave.Wave_read = wave.open(io.BytesIO(wav_file))
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wr.getsampwidth()),
            channels=wr.getnchannels(),
            rate=wr.getframerate(),
            output=True,
            output_device_index=device_index  # Use the specified or default device
        )
        chunk = 1024
        data = wr.readframes(chunk)
        while data:
            stream.write(data)
            data = wr.readframes(chunk)
        sleep(0.5)
        stream.close()
        p.terminate()

    def get_device_index(self, device_name: str) -> Optional[int]:
        """Finds the index of the audio device with the given name.

        Args:
            device_name (str): The name of the audio device.

        Returns:
            Optional[int]: The index of the device, or None if not found.
        """
        p = pyaudio.PyAudio()
        device_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['name'] == device_name:
                device_index = i
                break
        p.terminate()
        return device_index
