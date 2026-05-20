import json
from typing import List

from ..config import get_anthropic_key


def score_segments(transcript_segments: list, window_size: float = 10.0, window_step: float = 5.0, duration: float = 0) -> list:
    api_key = get_anthropic_key()
    if not api_key:
        return []

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    windows = _group_into_windows(transcript_segments, window_size, window_step, duration)

    all_scores = []
    batch_size = 10

    for i in range(0, len(windows), batch_size):
        batch = windows[i:i + batch_size]
        prompt = _build_prompt(batch)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        scores = _parse_scores(message.content[0].text, len(batch))
        all_scores.extend(scores)

    return all_scores


def _group_into_windows(segments: list, window_size: float, window_step: float, duration: float) -> list:
    if not segments and duration <= 0:
        return []

    if duration <= 0:
        duration = max(s["end"] for s in segments)

    windows = []
    t = 0.0
    while t + window_size <= duration:
        text_parts = []
        for seg in segments:
            if seg["end"] > t and seg["start"] < t + window_size:
                text_parts.append(seg["text"])
        windows.append({
            "start": t,
            "end": t + window_size,
            "text": "".join(text_parts),
        })
        t += window_step

    return windows


def _build_prompt(windows: list) -> str:
    lines = ["你是一个视频内容分析专家。以下是一段游戏/娱乐视频的转录文本片段。",
             "请为每个片段打分(0-10)，评估其作为精彩切片的价值。",
             "考虑因素：幽默感、激动时刻、惊喜事件、情绪高潮、经典台词、精彩操作、搞笑失误。",
             "", "片段列表："]

    for i, w in enumerate(windows):
        text = w["text"][:100] if w["text"] else "(无语音)"
        lines.append(f"[{i+1}] ({w['start']:.1f}s-{w['end']:.1f}s): {text}")

    lines.append("")
    lines.append('请只返回JSON格式: {"scores": [分数1, 分数2, ...]}')

    return "\n".join(lines)


def _parse_scores(response_text: str, expected_count: int) -> list:
    try:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(response_text[start:end])
            scores = data.get("scores", [])
            if len(scores) == expected_count:
                return [max(0, min(10, s)) / 10.0 for s in scores]
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    return [0.5] * expected_count
