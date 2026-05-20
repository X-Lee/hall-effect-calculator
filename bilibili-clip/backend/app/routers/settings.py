from fastapi import APIRouter

from ..models.schemas import ConfigUpdateRequest, ConfigResponse
from ..config import load_config, update_config, get_analysis_config, get_clip_config, get_whisper_config

router = APIRouter(prefix="/api/settings")


@router.get("", response_model=ConfigResponse)
async def get_settings():
    cfg = load_config()
    analysis = get_analysis_config()
    clip = get_clip_config()
    whisper = get_whisper_config()

    return ConfigResponse(
        anthropic_api_key_set=bool(cfg.get("anthropic_api_key")),
        whisper_model=whisper.get("model", "medium"),
        whisper_device=whisper.get("device", "auto"),
        weights=analysis.get("weights", {"danmaku": 0.4, "audio": 0.3, "ai": 0.3}),
        target_duration=clip.get("target_duration", 150.0),
        min_segment=clip.get("min_segment", 15.0),
        max_segment=clip.get("max_segment", 60.0),
    )


@router.post("")
async def update_settings(req: ConfigUpdateRequest):
    cfg = load_config()

    if req.anthropic_api_key is not None:
        cfg["anthropic_api_key"] = req.anthropic_api_key

    if req.whisper_model is not None:
        cfg.setdefault("whisper", {})["model"] = req.whisper_model

    if req.whisper_device is not None:
        cfg.setdefault("whisper", {})["device"] = req.whisper_device

    if req.weights is not None:
        cfg.setdefault("analysis", {})["weights"] = req.weights

    if req.target_duration is not None:
        cfg.setdefault("clip", {})["target_duration"] = req.target_duration

    update_config(cfg)
    return {"message": "配置已更新"}
