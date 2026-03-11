import pytest
from unittest.mock import patch, MagicMock
from vibevox.core.validator import validate_media_file, ValidationError


def _mock_ffprobe(returncode=0, duration=30.0):
    import json
    stdout = json.dumps({
        "format": {"duration": str(duration)},
        "streams": [{"codec_type": "audio"}],
    })
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = ""
    return result


def test_valid_file_returns_duration():
    with patch("subprocess.run", return_value=_mock_ffprobe(duration=30.0)):
        info = validate_media_file("audio.mp3")
    assert info["duration"] == pytest.approx(30.0)


def test_invalid_file_raises_validation_error():
    with patch("subprocess.run", return_value=_mock_ffprobe(returncode=1)):
        with pytest.raises(ValidationError, match="Not a valid media file"):
            validate_media_file("corrupt.mp3")


def test_duration_over_limit_raises_validation_error():
    with patch("subprocess.run", return_value=_mock_ffprobe(duration=3700.0)):
        with pytest.raises(ValidationError, match="exceeds 60 minute limit"):
            validate_media_file("long.mp3")


def test_ffprobe_not_found_raises_runtime_error():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError, match="ffprobe not found"):
            validate_media_file("audio.mp3")
