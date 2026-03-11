import io
import zipfile

from vibevox.core.formatters.txt import format_txt
from vibevox.core.formatters.srt import format_srt
from vibevox.core.formatters.vtt import format_vtt
from vibevox.core.formatters.json import format_json

SUPPORTED_FORMATS = {"txt", "srt", "vtt", "json"}


def format_segments(
    segments: list,
    fmt: str,
    diarization: bool = True,
    metadata: dict = None,
) -> str:
    """Dispatch to the correct formatter. Returns formatted string."""
    if fmt == "txt":
        return format_txt(segments, diarization=diarization)
    elif fmt == "srt":
        return format_srt(segments, diarization=diarization)
    elif fmt == "vtt":
        return format_vtt(segments, diarization=diarization)
    elif fmt == "json":
        return format_json(segments, metadata=metadata)
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose from: {SUPPORTED_FORMATS}")


def format_all_as_zip(
    segments: list,
    stem: str = "transcript",
    diarization: bool = True,
    metadata: dict = None,
) -> bytes:
    """Format segments in all 4 formats and return as a ZIP archive (bytes)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fmt in ("txt", "srt", "vtt", "json"):
            content = format_segments(segments, fmt=fmt, diarization=diarization, metadata=metadata)
            zf.writestr(f"{stem}.{fmt}", content)
    return buf.getvalue()
