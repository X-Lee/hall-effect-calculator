import yaml
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"

_config = None


def load_config() -> dict:
    global _config
    if _config is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _config = yaml.safe_load(f) or {}
        else:
            _config = {}
    return _config


def get_anthropic_key() -> str:
    cfg = load_config()
    return cfg.get("anthropic_api_key", "")


def get_analysis_config() -> dict:
    cfg = load_config()
    return cfg.get("analysis", {
        "window_size": 10.0,
        "window_step": 5.0,
        "weights": {"danmaku": 0.4, "audio": 0.3, "ai": 0.3},
    })


def get_clip_config() -> dict:
    cfg = load_config()
    return cfg.get("clip", {
        "target_duration": 150.0,
        "min_segment": 15.0,
        "max_segment": 60.0,
        "transition": "crossfade",
    })


def get_whisper_config() -> dict:
    cfg = load_config()
    return cfg.get("whisper", {
        "model": "medium",
        "language": "zh",
        "device": "auto",
    })


def update_config(updates: dict):
    global _config
    cfg = load_config()
    cfg.update(updates)
    _config = cfg
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
