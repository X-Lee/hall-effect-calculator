import numpy as np
import subprocess
import shutil
from pathlib import Path


def _get_ffmpeg_path() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    return "ffmpeg"


def extract_audio(video_path: str, output_path: str) -> str:
    ffmpeg = _get_ffmpeg_path()
    cmd = [
        ffmpeg, "-y",
        "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, timeout=300)
    return output_path


def compute_audio_energy(audio_path: str, window_size: float = 10.0, window_step: float = 5.0) -> list:
    import librosa

    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    duration = len(y) / sr

    window_samples = int(window_size * sr)
    step_samples = int(window_step * sr)

    energies = []
    pos = 0
    while pos + window_samples <= len(y):
        segment = y[pos:pos + window_samples]
        rms = np.sqrt(np.mean(segment ** 2))
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sr))
        energies.append({
            "start": pos / sr,
            "end": (pos + window_samples) / sr,
            "rms": float(rms),
            "spectral_centroid": float(spectral_centroid),
        })
        pos += step_samples

    if not energies:
        return []

    rms_values = [e["rms"] for e in energies]
    sc_values = [e["spectral_centroid"] for e in energies]

    rms_min, rms_max = min(rms_values), max(rms_values)
    sc_min, sc_max = min(sc_values), max(sc_values)

    for e in energies:
        rms_norm = (e["rms"] - rms_min) / (rms_max - rms_min + 1e-8)
        sc_norm = (e["spectral_centroid"] - sc_min) / (sc_max - sc_min + 1e-8)
        e["score"] = 0.7 * rms_norm + 0.3 * sc_norm

    return energies
