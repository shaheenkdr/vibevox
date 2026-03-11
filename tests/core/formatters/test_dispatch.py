import zipfile
import io
from vibevox.core.formatters import format_segments, format_all_as_zip

SEGMENTS = [
    {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello."},
]


def test_format_txt():
    result = format_segments(SEGMENTS, fmt="txt")
    assert "Hello." in result


def test_format_srt():
    result = format_segments(SEGMENTS, fmt="srt")
    assert "00:00:00,000" in result


def test_format_vtt():
    result = format_segments(SEGMENTS, fmt="vtt")
    assert "WEBVTT" in result


def test_format_json():
    import json
    result = format_segments(SEGMENTS, fmt="json")
    assert json.loads(result)["segments"][0]["Content"] == "Hello."


def test_invalid_format_raises():
    import pytest
    with pytest.raises(ValueError, match="Unsupported format"):
        format_segments(SEGMENTS, fmt="docx")


def test_format_all_as_zip_contains_all_files():
    data = format_all_as_zip(SEGMENTS, stem="transcript")
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = zf.namelist()
    assert "transcript.txt" in names
    assert "transcript.srt" in names
    assert "transcript.vtt" in names
    assert "transcript.json" in names
