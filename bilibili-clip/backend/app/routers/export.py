import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..models.schemas import ExportRequest
from ..services.task_manager import tasks, TaskStatus
from ..services.video_editor import generate_clip, OUTPUT_DIR

router = APIRouter(prefix="/api/export")


@router.post("/{task_id}/generate")
async def generate(task_id: str, req: ExportRequest):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    task = tasks[task_id]
    if task["status"] not in (TaskStatus.ANALYZED, TaskStatus.DONE):
        raise HTTPException(400, "请先完成分析")

    video_path = task["video_path"]
    segments = [s.model_dump() for s in req.segments]

    task["status"] = TaskStatus.EXPORTING
    task["export_progress"] = 0

    try:
        output_path = await asyncio.to_thread(
            generate_clip, video_path, segments, task_id, req.transition, req.quality
        )
        task["status"] = TaskStatus.DONE
        task["clip_path"] = output_path
        task["export_progress"] = 100
        return {"task_id": task_id, "status": "done", "download_url": f"/api/export/{task_id}/download"}
    except Exception as e:
        task["status"] = TaskStatus.ERROR
        raise HTTPException(500, f"导出失败: {str(e)}")


@router.get("/{task_id}/download")
async def download_clip(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    task = tasks[task_id]
    clip_path = task.get("clip_path")
    if not clip_path or not Path(clip_path).exists():
        raise HTTPException(404, "切片文件不存在")

    title = task.get("info", {}).get("title", "clip")
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-")[:50]
    filename = f"{safe_title}_highlight.mp4"

    return FileResponse(
        clip_path,
        media_type="video/mp4",
        filename=filename,
    )


@router.get("/{task_id}/preview")
async def preview_video(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    task = tasks[task_id]
    video_path = task.get("video_path")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(404, "视频文件不存在")

    return FileResponse(video_path, media_type="video/mp4")
