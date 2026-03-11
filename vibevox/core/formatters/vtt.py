from vibevox.core.formatters._time import seconds_to_timestamp


def format_vtt(segments: list, diarization: bool = True) -> str:
    """Format segments as WebVTT (.vtt) with timestamps."""
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = seconds_to_timestamp(seg["Start"], ".")
        end = seconds_to_timestamp(seg["End"], ".")
        content = seg["Content"]
        if diarization and seg.get("Speaker") is not None:
            content = f"[Speaker {seg['Speaker']}] {content}"
        lines.extend([f"{start} --> {end}", content, ""])
    return "\n".join(lines)
