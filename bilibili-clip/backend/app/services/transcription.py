import json
from pathlib import Path
from typing import Optional

from ..config import get_whisper_config

_model = None


def load_whisper_model():
    global _model
    if _model is not None:
        return _model

    import whisper

    cfg = get_whisper_config()
    model_name = cfg.get("model", "medium")
    device = cfg.get("device", "auto")

    if device == "auto":
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"

    _model = whisper.load_model(model_name, device=device)
    return _model


def transcribe_audio(audio_path: str, cache_path: Optional[str] = None) -> list:
    if cache_path:
        cache = Path(cache_path)
        if cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))

    model = load_whisper_model()
    cfg = get_whisper_config()

    result = model.transcribe(
        audio_path,
        language=cfg.get("language", "zh"),
        verbose=False,
    )

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })

    if cache_path:
        Path(cache_path).write_text(
            json.dumps(segments, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return segments
