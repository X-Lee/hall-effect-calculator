from pydantic import BaseModel
from typing import List, Optional


class VideoSubmitRequest(BaseModel):
    url: str


class VideoInfo(BaseModel):
    task_id: str
    title: str
    duration: float
    thumbnail_url: str
    bvid: str


class AnalysisStartRequest(BaseModel):
    weights: Optional[dict] = None
    target_duration: Optional[float] = None
    min_segment: Optional[float] = None
    max_segment: Optional[float] = None


class TimeWindow(BaseModel):
    start: float
    end: float
    danmaku_score: float
    audio_score: float
    ai_score: float
    combined_score: float
    transcript: str = ""


class Segment(BaseModel):
    start: float
    end: float
    score: float
    transcript_preview: str = ""


class AnalysisResult(BaseModel):
    task_id: str
    windows: List[TimeWindow]
    suggested_segments: List[Segment]
    total_duration: float


class ExportRequest(BaseModel):
    segments: List[Segment]
    transition: str = "crossfade"
    quality: str = "balanced"


class ProgressEvent(BaseModel):
    step: str
    status: str
    progress: float
    message: str


class ConfigUpdateRequest(BaseModel):
    anthropic_api_key: Optional[str] = None
    whisper_model: Optional[str] = None
    whisper_device: Optional[str] = None
    weights: Optional[dict] = None
    target_duration: Optional[float] = None


class ConfigResponse(BaseModel):
    anthropic_api_key_set: bool
    whisper_model: str
    whisper_device: str
    weights: dict
    target_duration: float
    min_segment: float
    max_segment: float
