import json
from vibevox.core.formatters.json import format_json

SEGMENTS = [
    {"Start": 0.0, "End": 5.4, "Speaker": 0, "Content": "Hello world."},
    {"Start": 5.4, "End": 10.0, "Speaker": 1, "Content": "How are you?"},
]


def test_json_is_valid_json():
    result = format_json(SEGMENTS)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_json_contains_segments():
    result = format_json(SEGMENTS)
    parsed = json.loads(result)
    assert len(parsed["segments"]) == 2
    assert parsed["segments"][0]["Content"] == "Hello world."


def test_json_contains_metadata():
    result = format_json(SEGMENTS, metadata={"duration_seconds": 10.0, "language": "en"})
    parsed = json.loads(result)
    assert parsed["metadata"]["duration_seconds"] == 10.0


def test_json_empty_segments():
    result = format_json([])
    parsed = json.loads(result)
    assert parsed["segments"] == []
