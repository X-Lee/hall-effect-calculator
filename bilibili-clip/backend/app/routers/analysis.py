import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..models.schemas import AnalysisStartRequest, AnalysisResult, TimeWindow, Segment
from ..config import get_analysis_config, get_clip_config
from ..services.task_manager import tasks, TaskStatus
from ..services.audio_analysis import extract_audio, compute_audio_energy
from ..services.score_fusion import compute_danmaku_density, fuse_scores, generate_time_windows
from ..services.transcription import transcribe_audio
from ..services.llm_scoring import score_segments
from ..services.segment_selector import select_segments

router = APIRouter(prefix="/api/analysis")

CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


@router.post("/{task_id}/start")
async def start_analysis(task_id: str, req: AnalysisStartRequest = None):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    task = tasks[task_id]
    if task["status"] not in (TaskStatus.DOWNLOADED, TaskStatus.ANALYZED):
        raise HTTPException(400, f"当前状态不允许分析: {task['status'].value}")

    task["status"] = TaskStatus.ANALYZING
    task["analysis_progress"] = {"step": "init", "progress": 0, "message": "开始分析..."}

    asyncio.create_task(_run_analysis(task_id, req))

    return {"task_id": task_id, "status": "analyzing"}


async def _run_analysis(task_id: str, req: AnalysisStartRequest = None):
    task = tasks[task_id]
    video_path = task["video_path"]
    danmaku = task.get("danmaku", [])
    duration = task["info"]["duration"]

    analysis_cfg = get_analysis_config()
    clip_cfg = get_clip_config()

    window_size = analysis_cfg.get("window_size", 10.0)
    window_step = analysis_cfg.get("window_step", 5.0)
    weights = req.weights if req and req.weights else analysis_cfg.get("weights")
    target_duration = req.target_duration if req and req.target_duration else clip_cfg.get("target_duration", 150.0)

    try:
        task["analysis_progress"] = {"step": "danmaku", "progress": 10, "message": "计算弹幕密度..."}
        danmaku_scores = compute_danmaku_density(danmaku, duration, window_size, window_step)
        time_windows = generate_time_windows(duration, window_size, window_step)

        task["analysis_progress"] = {"step": "audio", "progress": 25, "message": "提取音频..."}
        audio_path = str(CACHE_DIR / f"{task_id}_audio.wav")
        await asyncio.to_thread(extract_audio, video_path, audio_path)

        task["analysis_progress"] = {"step": "audio", "progress": 40, "message": "分析音频能量..."}
        audio_scores = await asyncio.to_thread(compute_audio_energy, audio_path, window_size, window_step)

        ai_scores = []
        try:
            task["analysis_progress"] = {"step": "transcription", "progress": 50, "message": "语音识别中(可能需要几分钟)..."}
            transcript_cache = str(CACHE_DIR / f"{task_id}_transcript.json")
            transcript = await asyncio.to_thread(transcribe_audio, audio_path, transcript_cache)

            task["analysis_progress"] = {"step": "ai_scoring", "progress": 75, "message": "AI语义打分..."}
            ai_scores = await asyncio.to_thread(score_segments, transcript, window_size, window_step, duration)
        except Exception:
            pass

        task["analysis_progress"] = {"step": "fusion", "progress": 90, "message": "融合评分..."}
        fused = fuse_scores(danmaku_scores, audio_scores, ai_scores, weights, time_windows)

        segments = select_segments(fused, target_duration)

        transcript_data = []
        try:
            tc = CACHE_DIR / f"{task_id}_transcript.json"
            if tc.exists():
                transcript_data = json.loads(tc.read_text(encoding="utf-8"))
        except Exception:
            pass

        for seg in segments:
            preview_parts = [t["text"] for t in transcript_data if t["end"] > seg["start"] and t["start"] < seg["end"]]
            seg["transcript_preview"] = "".join(preview_parts)[:80]

        task["analysis_result"] = {
            "windows": fused,
            "segments": segments,
        }
        task["status"] = TaskStatus.ANALYZED
        task["analysis_progress"] = {"step": "done", "progress": 100, "message": "分析完成"}

    except Exception as e:
        task["status"] = TaskStatus.ERROR
        task["analysis_progress"] = {"step": "error", "progress": 0, "message": f"分析失败: {str(e)}"}


@router.get("/{task_id}/progress")
async def analysis_progress(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    async def event_generator():
        while True:
            task = tasks.get(task_id)
            if not task:
                break
            progress = task.get("analysis_progress", {})
            yield {
                "event": "progress",
                "data": json.dumps(progress, ensure_ascii=False),
            }
            if progress.get("step") in ("done", "error"):
                break
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())


@router.get("/{task_id}/results", response_model=AnalysisResult)
async def get_results(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    task = tasks[task_id]
    if task["status"] != TaskStatus.ANALYZED:
        raise HTTPException(400, "分析尚未完成")

    result = task["analysis_result"]
    windows = [TimeWindow(**w) for w in result["windows"]]
    segments = [Segment(**s) for s in result["segments"]]
    total_duration = sum(s.end - s.start for s in segments)

    return AnalysisResult(
        task_id=task_id,
        windows=windows,
        suggested_segments=segments,
        total_duration=total_duration,
    )


@router.post("/{task_id}/rescore")
async def rescore(task_id: str, req: AnalysisStartRequest):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")
    task = tasks[task_id]
    if "analysis_result" not in task:
        raise HTTPException(400, "请先完成分析")

    weights = req.weights or get_analysis_config().get("weights")
    target_duration = req.target_duration or get_clip_config().get("target_duration", 150.0)

    fused = task["analysis_result"]["windows"]
    for w in fused:
        w_dm = weights.get("danmaku", 0.4)
        w_audio = weights.get("audio", 0.3)
        w_ai = weights.get("ai", 0.3)
        w["combined_score"] = w_dm * w["danmaku_score"] + w_audio * w["audio_score"] + w_ai * w["ai_score"]

    segments = select_segments(fused, target_duration)
    task["analysis_result"]["segments"] = segments

    return {"segments": segments, "total_duration": sum(s["end"] - s["start"] for s in segments)}
