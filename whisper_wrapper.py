import torch 
from transformers import pipeline
from ModelInterfaces import IASRModel
from typing import Union
import numpy as np 

class WhisperASRModel(IASRModel):
    def __init__(self, model_name="openai/whisper-base"):
        self.asr = pipeline("automatic-speech-recognition", model=model_name, return_timestamps="word")
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
        # 'audio' can be a path to a file or a numpy array of audio samples.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        result = self.asr(audio[0])
        self._transcript = result["text"]
        # self._word_locations = [{"word":word_info["text"], "start_ts":word_info["timestamp"][0]*self.sample_rate,
        #                          "end_ts":word_info["timestamp"][1]*self.sample_rate} for word_info in result["chunks"]]
        
        # compute audio length in samples for default end-timestamp
        total_samples = audio.shape[-1]  # number of samples in the input array

        # guard against None timestamps
        self._word_locations = [
        {
            "word": word_info["text"],
            "start_ts": int(word_info["timestamp"][0] * self.sample_rate)
                        if word_info["timestamp"][0] is not None else 0,
            "end_ts":   int(word_info["timestamp"][1] * self.sample_rate)
                        if word_info["timestamp"][1] is not None else total_samples
        }
        for word_info in result["chunks"]
        ]

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:
        
        return self._word_locations