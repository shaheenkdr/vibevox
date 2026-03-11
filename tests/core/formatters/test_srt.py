from vibevox.core.formatters.srt import format_srt

SEGMENTS = [
    {"Start": 0.0, "End": 5.4, "Speaker": 0, "Content": "Hello world."},
    {"Start": 5.4, "End": 10.123, "Speaker": 1, "Content": "How are you?"},
]


def test_srt_has_index_numbers():
    result = format_srt(SEGMENTS)
    assert result.startswith("1\n")
    assert "\n2\n" in result


def test_srt_timestamp_format():
    result = format_srt(SEGMENTS)
    assert "00:00:00,000 --> 00:00:05,400" in result


def test_srt_with_diarization():
    result = format_srt(SEGMENTS, diarization=True)
    assert "[Speaker 0]" in result


def test_srt_without_diarization():
    result = format_srt(SEGMENTS, diarization=False)
    assert "[Speaker" not in result


def test_srt_empty_segments():
    assert format_srt([]) == ""
