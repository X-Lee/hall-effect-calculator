import subprocess
import shutil
from pathlib import Path
from typing import List

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


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


def generate_clip(video_path: str, segments: list, task_id: str, transition: str = "crossfade", quality: str = "balanced") -> str:
    output_path = OUTPUT_DIR / f"{task_id}_clip.mp4"
    ffmpeg = _get_ffmpeg_path()

    crf = {"fast": "28", "balanced": "23", "high": "18"}.get(quality, "23")

    if len(segments) == 1:
        seg = segments[0]
        cmd = [
            ffmpeg, "-y",
            "-ss", str(seg["start"]),
            "-i", video_path,
            "-t", str(seg["end"] - seg["start"]),
            "-c:v", "libx264", "-crf", crf,
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, timeout=600)
        return str(output_path)

    temp_dir = OUTPUT_DIR / f"{task_id}_temp"
    temp_dir.mkdir(exist_ok=True)

    segment_files = []
    for i, seg in enumerate(segments):
        seg_path = temp_dir / f"seg_{i:03d}.mp4"
        cmd = [
            ffmpeg, "-y",
            "-ss", str(seg["start"]),
            "-i", video_path,
            "-t", str(seg["end"] - seg["start"]),
            "-c:v", "libx264", "-crf", crf,
            "-c:a", "aac", "-b:a", "128k",
            str(seg_path),
        ]
        subprocess.run(cmd, capture_output=True, timeout=300)
        segment_files.append(seg_path)

    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for seg_path in segment_files:
            f.write(f"file '{seg_path.as_posix()}'\n")

    cmd = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264", "-crf", crf,
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, capture_output=True, timeout=600)

    shutil.rmtree(temp_dir, ignore_errors=True)

    return str(output_path)
