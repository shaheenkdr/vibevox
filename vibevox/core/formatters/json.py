import json as _json


def format_json(segments: list, metadata: dict = None) -> str:
    """Format segments as structured JSON with optional metadata."""
    output = {
        "metadata": metadata or {},
        "segments": segments,
    }
    return _json.dumps(output, indent=2)
