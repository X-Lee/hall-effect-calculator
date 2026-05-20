import numpy as np
from scipy.ndimage import gaussian_filter1d
from typing import List

from ..config import get_analysis_config


def compute_danmaku_density(danmaku_list: list, duration: float, window_size: float = 10.0, window_step: float = 5.0) -> list:
    windows = []
    t = 0.0
    while t + window_size <= duration:
        count = sum(1 for d in danmaku_list if t <= d["time"] < t + window_size)
        windows.append({
            "start": t,
            "end": t + window_size,
            "count": count,
        })
        t += window_step

    if not windows:
        return []

    counts = [w["count"] for w in windows]
    max_count = max(counts) if max(counts) > 0 else 1
    for w in windows:
        w["score"] = w["count"] / max_count

    return windows


def generate_time_windows(duration: float, window_size: float = 10.0, window_step: float = 5.0) -> list:
    windows = []
    t = 0.0
    while t + window_size <= duration:
        windows.append({"start": t, "end": t + window_size})
        t += window_step
    return windows


def fuse_scores(danmaku_scores: list, audio_scores: list, ai_scores: list, weights: dict = None, time_windows: list = None) -> list:
    if weights is None:
        cfg = get_analysis_config()
        weights = cfg.get("weights", {"danmaku": 0.4, "audio": 0.3, "ai": 0.3})

    n = len(danmaku_scores) if danmaku_scores else (len(audio_scores) if audio_scores else 0)
    if n == 0:
        return []

    if danmaku_scores:
        dm = np.array([w["score"] for w in danmaku_scores])
    else:
        dm = np.zeros(n)

    audio = np.zeros(n)
    if audio_scores:
        audio_raw = np.array([w["score"] for w in audio_scores[:n]])
        if len(audio_raw) < n:
            audio[:len(audio_raw)] = audio_raw
        else:
            audio = audio_raw[:n]

    ai = np.full(n, 0.5)
    if ai_scores:
        ai_raw = np.array(ai_scores[:n])
        if len(ai_raw) < n:
            ai[:len(ai_raw)] = ai_raw
        else:
            ai = ai_raw[:n]

    w_dm = weights.get("danmaku", 0.4)
    w_audio = weights.get("audio", 0.3)
    w_ai = weights.get("ai", 0.3)

    if not danmaku_scores and not ai_scores:
        w_dm = 0
        w_audio = 1.0
        w_ai = 0
    elif not danmaku_scores:
        total = w_audio + w_ai
        w_dm = 0
        w_audio = w_audio / total
        w_ai = w_ai / total
    elif not ai_scores:
        total = w_dm + w_audio
        w_dm /= total
        w_audio /= total
        w_ai = 0

    combined = w_dm * dm + w_audio * audio + w_ai * ai
    combined = gaussian_filter1d(combined, sigma=1.0)

    combined_min = combined.min()
    combined_max = combined.max()
    if combined_max > combined_min:
        combined = (combined - combined_min) / (combined_max - combined_min)

    ref_windows = danmaku_scores if danmaku_scores else (audio_scores if audio_scores else time_windows or [])

    results = []
    for i in range(n):
        results.append({
            "start": ref_windows[i]["start"],
            "end": ref_windows[i]["end"],
            "danmaku_score": float(dm[i]),
            "audio_score": float(audio[i]),
            "ai_score": float(ai[i]),
            "combined_score": float(combined[i]),
        })

    return results
