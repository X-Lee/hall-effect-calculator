import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..models.schemas import VideoSubmitRequest, VideoInfo
from ..services.bilibili import download_video, get_video_info, parse_bilibili_url
from ..services.task_manager import tasks, TaskStatus

router = APIRouter(prefix="/api/video")


@router.post("/submit", response_model=VideoInfo)
async def submit_video(req: VideoSubmitRequest):
    parsed = parse_bilibili_url(req.url)
    if not parsed:
        raise HTTPException(400, "无效的B站链接，请输入正确的视频URL")

    bvid = parsed["bvid"]
    page = parsed["page"]

    info = await get_video_info(bvid, page)
    if not info:
        raise HTTPException(400, "无法获取视频信息，请检查链接是否正确")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": TaskStatus.PENDING,
        "bvid": bvid,
        "page": page,
        "info": info,
        "progress": 0,
        "message": "等待下载",
    }

    asyncio.create_task(_background_download(task_id, bvid, page))

    return VideoInfo(
        task_id=task_id,
        title=info["title"],
        duration=info["duration"],
        thumbnail_url=info["thumbnail"],
        bvid=bvid,
    )


async def _background_download(task_id: str, bvid: str, page: int = 1):
    tasks[task_id]["status"] = TaskStatus.DOWNLOADING
    tasks[task_id]["message"] = "正在下载视频..."
    try:
        result = await asyncio.to_thread(download_video, bvid, task_id, page)
        tasks[task_id]["status"] = TaskStatus.DOWNLOADED
        tasks[task_id]["video_path"] = result["video_path"]
        tasks[task_id]["danmaku"] = result.get("danmaku", [])
        tasks[task_id]["message"] = "下载完成"
        tasks[task_id]["progress"] = 100
    except Exception as e:
        tasks[task_id]["status"] = TaskStatus.ERROR
        tasks[task_id]["message"] = f"下载失败: {str(e)}"


@router.get("/{task_id}/info")
async def get_task_info(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")
    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"].value,
        "progress": task.get("progress", 0),
        "message": task.get("message", ""),
        "info": task.get("info"),
        "analysis_progress": task.get("analysis_progress"),
    }


@router.get("/{task_id}/stream")
async def stream_progress(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")

    async def event_generator():
        while True:
            task = tasks.get(task_id)
            if not task:
                break
            yield {
                "event": "progress",
                "data": f'{{"status": "{task["status"].value}", "progress": {task.get("progress", 0)}, "message": "{task.get("message", "")}"}}',
            }
            if task["status"] in (TaskStatus.DOWNLOADED, TaskStatus.ERROR):
                break
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
