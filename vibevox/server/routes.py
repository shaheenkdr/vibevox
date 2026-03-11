import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from vibevox.core.converter import convert_to_wav
from vibevox.core.formatters import format_segments
from vibevox.core.transcriber import DEFAULT_MODEL, Transcriber
from vibevox.core.validator import ValidationError, validate_media_file

router = APIRouter()

VALID_FORMATS = {"txt", "srt", "vtt", "json"}

_transcriber: Optional[Transcriber] = None


def _get_transcriber(model: str = DEFAULT_MODEL, device: str = "auto") -> Transcriber:
    global _transcriber
    if _transcriber is None:
        _transcriber = Transcriber(model_id=model, device=device)
    return _transcriber


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/info")
def info():
    return {
        "model": DEFAULT_MODEL,
        "supported_formats": sorted(VALID_FORMATS),
        "max_duration_seconds": 3600,
    }


@router.post("/transcribe")
def transcribe(
    file: UploadFile = File(...),
    format: str = Form("txt"),
    language: Optional[str] = Form(None),
    diarization: bool = Form(True),
    decode: str = Form("greedy"),
):
    """Transcribe an uploaded audio or video file."""
    if format not in VALID_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format {format!r}. Choose from: {', '.join(sorted(VALID_FORMATS))}",
        )

    suffix = Path(file.filename or "upload").suffix or ".bin"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    tmp_wav = None
    try:
        try:
            file_info = validate_media_file(tmp_path)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        duration = file_info["duration"]

        try:
            wav_path = convert_to_wav(tmp_path)
            if wav_path != tmp_path:
                tmp_wav = wav_path
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

        try:
            transcriber = _get_transcriber()
            segments = transcriber.transcribe(
                wav_path,
                language=language,
                diarization=diarization,
                decode=decode,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

        metadata = {
            "duration_seconds": duration,
            "model": DEFAULT_MODEL,
            "language": language or "auto",
        }
        transcript = format_segments(
            segments, fmt=format, diarization=diarization, metadata=metadata
        )

        return {
            "format": format,
            "duration_seconds": duration,
            "language_detected": language or "auto",
            "transcript": transcript,
            "segments": segments,
        }

    finally:
        Path(tmp_path).unlink(missing_ok=True)
        if tmp_wav and Path(tmp_wav).exists():
            Path(tmp_wav).unlink(missing_ok=True)
