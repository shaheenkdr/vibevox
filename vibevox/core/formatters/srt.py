def _seconds_to_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds % 1) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_srt(segments: list, diarization: bool = True) -> str:
    """Format segments as SubRip (.srt) with timestamps."""
    if not segments:
        return ""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _seconds_to_srt_time(seg["Start"])
        end = _seconds_to_srt_time(seg["End"])
        content = seg["Content"]
        if diarization and seg.get("Speaker") is not None:
            content = f"[Speaker {seg['Speaker']}] {content}"
        lines.extend([str(i), f"{start} --> {end}", content, ""])
    return "\n".join(lines)
