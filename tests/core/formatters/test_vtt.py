from vibevox.core.formatters.vtt import format_vtt

SEGMENTS = [
    {"Start": 0.0, "End": 5.4, "Speaker": 0, "Content": "Hello world."},
    {"Start": 5.4, "End": 10.123, "Speaker": 1, "Content": "How are you?"},
]


def test_vtt_starts_with_webvtt_header():
    result = format_vtt(SEGMENTS)
    assert result.startswith("WEBVTT")


def test_vtt_timestamp_format():
    result = format_vtt(SEGMENTS)
    assert "00:00:00.000 --> 00:00:05.400" in result


def test_vtt_with_diarization():
    result = format_vtt(SEGMENTS, diarization=True)
    assert "[Speaker 0]" in result


def test_vtt_without_diarization():
    result = format_vtt(SEGMENTS, diarization=False)
    assert "[Speaker" not in result


def test_vtt_empty_segments():
    result = format_vtt([])
    assert result.startswith("WEBVTT")
