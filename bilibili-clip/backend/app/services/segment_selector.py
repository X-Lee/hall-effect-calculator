from typing import List
from ..config import get_clip_config


def select_segments(scored_windows: list, target_duration: float = None, min_segment: float = None, max_segment: float = None) -> list:
    cfg = get_clip_config()
    if target_duration is None:
        target_duration = cfg.get("target_duration", 150.0)
    if min_segment is None:
        min_segment = cfg.get("min_segment", 15.0)
    if max_segment is None:
        max_segment = cfg.get("max_segment", 60.0)

    if not scored_windows:
        return []

    scores = [w["combined_score"] for w in scored_windows]
    mean_score = sum(scores) / len(scores)
    std_score = (sum((s - mean_score) ** 2 for s in scores) / len(scores)) ** 0.5
    threshold = mean_score + 0.3 * std_score

    candidates = _merge_windows(scored_windows, threshold, min_segment, max_segment)

    candidates.sort(key=lambda s: s["score"], reverse=True)

    selected = []
    total = 0.0
    for seg in candidates:
        seg_duration = seg["end"] - seg["start"]
        if total + seg_duration > target_duration:
            remaining = target_duration - total
            if remaining >= min_segment:
                seg["end"] = seg["start"] + remaining
                selected.append(seg)
                total += remaining
            break
        selected.append(seg)
        total += seg_duration

    if total < target_duration * 0.5 and candidates:
        threshold = mean_score
        candidates = _merge_windows(scored_windows, threshold, min_segment, max_segment)
        candidates.sort(key=lambda s: s["score"], reverse=True)
        selected = []
        total = 0.0
        for seg in candidates:
            seg_duration = seg["end"] - seg["start"]
            if total + seg_duration > target_duration:
                break
            selected.append(seg)
            total += seg_duration

    selected.sort(key=lambda s: s["start"])
    return selected


def _merge_windows(windows: list, threshold: float, min_segment: float, max_segment: float) -> list:
    above = [w for w in windows if w["combined_score"] >= threshold]
    if not above:
        return []

    segments = []
    current_start = above[0]["start"]
    current_end = above[0]["end"]
    current_scores = [above[0]["combined_score"]]

    for w in above[1:]:
        if w["start"] <= current_end:
            current_end = w["end"]
            current_scores.append(w["combined_score"])
        else:
            seg_duration = current_end - current_start
            if seg_duration >= min_segment:
                if seg_duration > max_segment:
                    current_end = current_start + max_segment
                segments.append({
                    "start": current_start,
                    "end": current_end,
                    "score": sum(current_scores) / len(current_scores),
                })
            current_start = w["start"]
            current_end = w["end"]
            current_scores = [w["combined_score"]]

    seg_duration = current_end - current_start
    if seg_duration >= min_segment:
        if seg_duration > max_segment:
            current_end = current_start + max_segment
        segments.append({
            "start": current_start,
            "end": current_end,
            "score": sum(current_scores) / len(current_scores),
        })

    return segments
