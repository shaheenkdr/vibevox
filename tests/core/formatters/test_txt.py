from vibevox.core.formatters.txt import format_txt

SEGMENTS = [
    {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello world."},
    {"Start": 5.0, "End": 10.0, "Speaker": 1, "Content": "How are you?"},
]


def test_with_diarization():
    result = format_txt(SEGMENTS, diarization=True)
    assert "[Speaker 0]" in result
    assert "[Speaker 1]" in result
    assert "Hello world." in result
    assert "How are you?" in result


def test_without_diarization():
    result = format_txt(SEGMENTS, diarization=False)
    assert "[Speaker" not in result
    assert "Hello world." in result
    assert "How are you?" in result


def test_empty_segments():
    assert format_txt([], diarization=True) == ""


def test_none_speaker_skips_label():
    segs = [{"Start": 0.0, "End": 5.0, "Speaker": None, "Content": "Hello."}]
    result = format_txt(segs, diarization=True)
    assert "[Speaker" not in result
    assert "Hello." in result
