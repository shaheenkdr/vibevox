import pytest
from unittest.mock import patch, MagicMock
from vibevox.core.converter import convert_to_wav, NATIVE_FORMATS


def _mock_ffprobe_info(sample_rate=24000, channels=1):
    import json
    stdout = json.dumps({
        "streams": [{"codec_type": "audio", "sample_rate": str(sample_rate), "channels": channels}],
        "format": {},
    })
    r = MagicMock()
    r.returncode = 0
    r.stdout = stdout
    return r


def _mock_ffmpeg_ok():
    r = MagicMock()
    r.returncode = 0
    r.stderr = ""
    return r


def test_native_format_correct_spec_no_conversion(tmp_path):
    wav = tmp_path / "audio.wav"
    wav.write_bytes(b"fake")
    with patch("subprocess.run", return_value=_mock_ffprobe_info(24000, 1)) as mock_run:
        result = convert_to_wav(str(wav))
    assert result == str(wav)
    assert all("ffmpeg" not in str(c) for c in mock_run.call_args_list)


def test_native_format_wrong_sample_rate_converts(tmp_path):
    wav = tmp_path / "audio.wav"
    wav.write_bytes(b"fake")
    with patch("subprocess.run", side_effect=[
        _mock_ffprobe_info(44100, 1),
        _mock_ffmpeg_ok(),
    ]):
        result = convert_to_wav(str(wav))
    assert result.endswith(".wav")
    assert result != str(wav)


def test_video_file_always_converts(tmp_path):
    mp4 = tmp_path / "video.mp4"
    mp4.write_bytes(b"fake")
    with patch("subprocess.run", return_value=_mock_ffmpeg_ok()):
        result = convert_to_wav(str(mp4))
    assert result.endswith(".wav")
    assert result != str(mp4)


def test_ffmpeg_failure_raises_runtime_error(tmp_path):
    mp4 = tmp_path / "video.mp4"
    mp4.write_bytes(b"fake")
    bad = MagicMock()
    bad.returncode = 1
    bad.stderr = "codec error"
    with patch("subprocess.run", return_value=bad):
        with pytest.raises(RuntimeError, match="ffmpeg conversion failed"):
            convert_to_wav(str(mp4))


def test_native_formats_set_contains_expected():
    assert ".wav" in NATIVE_FORMATS
    assert ".mp3" in NATIVE_FORMATS
    assert ".mp4" not in NATIVE_FORMATS
