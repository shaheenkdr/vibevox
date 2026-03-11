def seconds_to_timestamp(seconds: float, ms_sep: str) -> str:
    """
    Convert a float seconds value to a subtitle timestamp string.

    Args:
        seconds: Time in seconds.
        ms_sep:  Separator between seconds and milliseconds (',' for SRT, '.' for VTT).

    Returns:
        Timestamp string in the form HH:MM:SS<ms_sep>mmm.
        Handles rounding correctly so milliseconds never exceed 999.
    """
    total_ms = round(seconds * 1000)
    millis = total_ms % 1000
    total_secs = total_ms // 1000
    secs = total_secs % 60
    total_mins = total_secs // 60
    mins = total_mins % 60
    hours = total_mins // 60
    return f"{hours:02d}:{mins:02d}:{secs:02d}{ms_sep}{millis:03d}"
