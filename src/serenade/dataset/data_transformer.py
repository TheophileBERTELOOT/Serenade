import os
from pathlib import Path
from typing import Any

import librosa
import matplotlib.pyplot as plt
import numpy as np


class DataTransformer:
    def __init__(self, audios_dir: Path, spectrograms_dir: Path) -> None:
        self.audios_dir = audios_dir
        self.spectrograms_dir = spectrograms_dir

    def load_and_pad_audio(
        self, file_path: Path, target_duration: int = 10, sr: int = 22050
    ) -> np.ndarray:
        y, _ = librosa.load(file_path, sr=sr)
        max_length = int(sr * target_duration)
        if len(y) > max_length:
            y = y[:max_length]
        else:
            y = np.pad(y, (0, max_length - len(y)))
        return y

    def audio_to_mel_spectrogram(
        self, file_path: Path, n_mels: int = 128, duration: int = 10, sr: int = 22050
    ) -> np.ndarray:
        y = self.load_and_pad_audio(file_path, target_duration=duration, sr=sr)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)  # Convertir en dB

        return mel_spec_db

    def visualize_spectrogram(
        self, mel_spec: np.ndarray, sr: int = 22050, hop_length: int = 512
    ) -> None:
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(
            mel_spec, sr=sr, hop_length=hop_length, x_axis="time", y_axis="mel"
        )
        plt.colorbar(format="%+2.0f dB")
        plt.title("Mel Spectrogram")
        plt.tight_layout()
        plt.show()

    def save_as_image(self, mel_spec_db: np.ndarray, output_path: Path) -> None:
        plt.figure(figsize=(10, 4))
        plt.axis("off")  # Supprimer les axes
        plt.imshow(
            mel_spec_db, aspect="auto", origin="lower", cmap="viridis"
        )  # Spectrogramme en couleurs
        plt.tight_layout()
        plt.savefig(
            output_path, bbox_inches="tight", pad_inches=0, format="png"
        )  # Sauvegarder en PNG
        plt.close()

    def transform_data(self) -> None:
        for audio_path in self.audios_dir.iterdir():
            fname = ".".join(audio_path.name.split(".")[:-1])  # Remove extension
            spectro = self.audio_to_mel_spectrogram(audio_path)
            self.save_as_image(spectro, self.spectrograms_dir.joinpath(f"{fname}.png"))
