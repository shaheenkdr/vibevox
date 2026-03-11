import json
import subprocess
import tempfile
from pathlib import Path

from vibevox.core.logger import get_logger

logger = get_logger(__name__)

NATIVE_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".opus", ".webm", ".m4a"}


def _get_audio_info(path: str) -> dict:
    """Run ffprobe to get sample_rate and channels for the first audio stream."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_streams", "-select_streams", "a:0",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    info = json.loads(result.stdout)
    streams = info.get("streams", [])
    if not streams:
        return {"sample_rate": 0, "channels": 0}
    return {
        "sample_rate": int(streams[0].get("sample_rate", 0)),
        "channels": int(streams[0].get("channels", 0)),
    }


def _run_ffmpeg_convert(input_path: str, output_path: str) -> None:
    """Convert input to 24kHz mono WAV using ffmpeg."""
    result = subprocess.run(
        ["ffmpeg", "-i", input_path, "-ar", "24000", "-ac", "1", "-y", output_path],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")


def convert_to_wav(input_path: str) -> str:
    """
    Ensure the audio is 24kHz mono WAV for VibeVoice.

    - Native formats (wav/mp3/flac/etc): pass through if already 24kHz mono,
      otherwise re-encode.
    - Non-native formats (mp4/mkv/etc): always extract audio and convert.

    Returns the path to a 24kHz mono WAV file.
    The returned path may equal input_path (no conversion needed) or be a
    new temp file that the caller is responsible for cleaning up.
    """
    path = Path(input_path)
    suffix = path.suffix.lower()

    if suffix in NATIVE_FORMATS:
        info = _get_audio_info(input_path)
        if info["sample_rate"] == 24000 and info["channels"] == 1:
            logger.debug(f"No conversion needed: {input_path}")
            return input_path

    logger.debug(f"Converting to 24kHz mono WAV: {input_path}")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    _run_ffmpeg_convert(input_path, tmp.name)
    return tmp.name
