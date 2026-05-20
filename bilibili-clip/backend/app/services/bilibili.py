import re
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional

import httpx
import lxml.etree as ET

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def _get_ffmpeg_dir() -> Optional[str]:
    path = shutil.which("ffmpeg")
    if path:
        return str(Path(path).parent)
    try:
        import imageio_ffmpeg
        return str(Path(imageio_ffmpeg.get_ffmpeg_exe()).parent)
    except ImportError:
        pass
    return None


def parse_bilibili_url(url: str) -> Optional[dict]:
    patterns = [
        r"bilibili\.com/video/(BV[\w]+)",
        r"b23\.tv/(BV[\w]+)",
        r"(BV[\w]{10})",
    ]
    bvid = None
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            bvid = m.group(1)
            break
    if not bvid:
        return None

    page = 1
    page_match = re.search(r"[?&]p=(\d+)", url)
    if page_match:
        page = int(page_match.group(1))

    return {"bvid": bvid, "page": page}


async def get_video_info(bvid: str, page: int = 1) -> Optional[dict]:
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        data = resp.json()

    if data.get("code") != 0:
        return None

    info = data["data"]
    pages = info.get("pages", [])

    cid = info["cid"]
    duration = info["duration"]
    part_title = ""

    if pages and 1 <= page <= len(pages):
        page_info = pages[page - 1]
        cid = page_info["cid"]
        duration = page_info["duration"]
        part_title = page_info.get("part", "")

    title = info["title"]
    if part_title:
        title = f"{title} - {part_title}"

    return {
        "title": title,
        "duration": duration,
        "thumbnail": info["pic"],
        "cid": cid,
        "page": page,
        "total_pages": len(pages),
        "desc": info.get("desc", ""),
    }


def download_video(bvid: str, task_id: str, page: int = 1) -> dict:
    output_path = UPLOAD_DIR / f"{task_id}.mp4"
    video_url = f"https://www.bilibili.com/video/{bvid}?p={page}"

    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        "--no-playlist",
        "--playlist-items", str(page),
        "--socket-timeout", "60",
        "--retries", "5",
        "--fragment-retries", "5",
    ]

    ffmpeg_dir = _get_ffmpeg_dir()
    if ffmpeg_dir:
        cmd.extend(["--ffmpeg-location", ffmpeg_dir])

    cmd.append(video_url)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate(timeout=7200)
    if process.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {stderr[:500]}")

    if not output_path.exists():
        candidates = list(UPLOAD_DIR.glob(f"{task_id}.*"))
        if candidates:
            output_path = candidates[0]
        else:
            raise RuntimeError("下载完成但未找到输出文件")

    danmaku = fetch_danmaku(bvid, page)

    return {
        "video_path": str(output_path),
        "danmaku": danmaku,
    }


def fetch_danmaku(bvid: str, page: int = 1) -> list:
    import httpx as httpx_sync

    info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com",
    }

    with httpx_sync.Client() as client:
        resp = client.get(info_url, headers=headers)
        data = resp.json()

    if data.get("code") != 0:
        return []

    pages = data["data"].get("pages", [])
    if pages and 1 <= page <= len(pages):
        cid = pages[page - 1]["cid"]
    else:
        cid = data["data"]["cid"]

    dm_url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"

    with httpx_sync.Client() as client:
        resp = client.get(dm_url, headers=headers)

    try:
        root = ET.fromstring(resp.content)
        danmaku_list = []
        for d in root.findall(".//d"):
            attrs = d.get("p", "").split(",")
            if len(attrs) >= 1:
                danmaku_list.append({
                    "time": float(attrs[0]),
                    "text": d.text or "",
                })
        return sorted(danmaku_list, key=lambda x: x["time"])
    except Exception:
        return []
