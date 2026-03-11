from vibevox.core.formatters._time import seconds_to_timestamp


def format_srt(segments: list, diarization: bool = True) -> str:
    """Format segments as SubRip (.srt) with timestamps."""
    if not segments:
        return ""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = seconds_to_timestamp(seg["Start"], ",")
        end = seconds_to_timestamp(seg["End"], ",")
        content = seg["Content"]
        if diarization and seg.get("Speaker") is not None:
            content = f"[Speaker {seg['Speaker']}] {content}"
        lines.extend([str(i), f"{start} --> {end}", content, ""])
    return "\n".join(lines)
