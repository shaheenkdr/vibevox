import json
import subprocess
from vibevox.core.logger import get_logger

logger = get_logger(__name__)

MAX_DURATION_SECONDS = 3600  # 60 minutes


class ValidationError(ValueError):
    """Raised when a media file fails validation."""


def validate_media_file(path: str) -> dict:
    """
    Validate that path is a readable media file under the duration limit.

    Returns dict with 'duration' (float, seconds) on success.
    Raises ValidationError for invalid files or duration exceeded.
    Raises RuntimeError if ffprobe is not installed.
    """
    logger.debug(f"Validating: {path}")
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffprobe not found. Install ffmpeg: https://ffmpeg.org/download.html"
        )

    if result.returncode != 0:
        raise ValidationError(f"Not a valid media file: {path}")

    info = json.loads(result.stdout)
    duration = float(info["format"].get("duration", 0))

    if duration > MAX_DURATION_SECONDS:
        minutes = duration / 60
        raise ValidationError(
            f"File duration {minutes:.1f} minutes exceeds 60 minute limit"
        )

    logger.debug(f"Valid media file: {path}, duration={duration:.1f}s")
    return {"duration": duration, "info": info}
