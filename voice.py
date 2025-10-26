import os
import time
import torch
import torchaudio as ta
import numpy as np
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

class VoiceGenerator:
    def __init__(self, device="cuda", language="ru"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.language = language
        self.model = None
        self.is_loaded = False


    def load_model(self):
        """Загрузка модели (вызывается автоматически при первой генерации)"""
        if self.is_loaded:
            return

        self.model = ChatterboxMultilingualTTS.from_pretrained(self.device)
        self.is_loaded = True

    def generate_speech(self, text, reference_file=None):
        """
        Основная функция генерации речи
        """
        if not self.is_loaded:
            self.load_model()

        if reference_file and not os.path.exists(reference_file):
            reference_file = None

        start_time = time.time()

        if reference_file:
            audio = self.model.generate(
                text=text,
                language_id=self.language,
                audio_prompt_path=reference_file
            )
        else:
            audio = self.model.generate(
                text=text,
                language_id=self.language
            )

        gen_time = time.time() - start_time
        sr = getattr(self.model, "sr", 24000)
        return audio, sr, gen_time

    def play_audio(self, audio, sample_rate):
        """Воспроизведение аудио"""
        if audio is None:
            return False

        import sounddevice as sd
        wav = audio.squeeze().cpu().numpy().astype(np.float32)
        wav = wav / (np.max(np.abs(wav)) + 1e-9)

        sd.play(wav, sample_rate)
        sd.wait()
        return True

    def save_audio(self, audio, sample_rate, filename):
        """Сохранение аудио в файл"""
        if audio is None:
            return False

        wav = audio.detach().cpu()
        if wav.ndim == 1:
            wav = wav.unsqueeze(0)

        ta.save(filename, wav, sample_rate)
        return True