def format_txt(segments: list, diarization: bool = True) -> str:
    """Format segments as plain text, one line per segment."""
    lines = []
    for seg in segments:
        content = seg["Content"]
        if diarization and seg.get("Speaker") is not None:
            content = f"[Speaker {seg['Speaker']}] {content}"
        lines.append(content)
    return "\n".join(lines)
