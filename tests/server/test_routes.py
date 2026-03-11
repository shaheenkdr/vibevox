from unittest.mock import MagicMock, patch

import pytest

import vibevox.server.routes as routes_module

MOCK_SEGMENTS = [
    {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello world."},
]


@pytest.fixture(autouse=True)
def reset_transcriber():
    """Ensure the module-level transcriber singleton is cleared between tests."""
    routes_module._transcriber = None
    yield
    routes_module._transcriber = None


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from vibevox.server.app import app
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_info(client):
    r = client.get("/info")
    assert r.status_code == 200
    data = r.json()
    assert data["model"] == "microsoft/VibeVoice-ASR-HF"
    assert "txt" in data["supported_formats"]
    assert data["max_duration_seconds"] == 3600


def test_transcribe_invalid_format(client):
    r = client.post(
        "/transcribe",
        data={"format": "pdf"},
        files={"file": ("test.wav", b"fake", "audio/wav")},
    )
    assert r.status_code == 400
    assert "Invalid format" in r.json()["detail"]


def test_transcribe_invalid_file(client):
    from vibevox.core.validator import ValidationError

    with patch("vibevox.server.routes.validate_media_file", side_effect=ValidationError("Not a valid media file")):
        r = client.post(
            "/transcribe",
            files={"file": ("test.wav", b"not-a-real-file", "audio/wav")},
        )
    assert r.status_code == 400
    assert "Not a valid media file" in r.json()["detail"]


def test_transcribe_success(client):
    mock_transcriber = MagicMock()
    mock_transcriber.transcribe.return_value = MOCK_SEGMENTS

    with (
        patch("vibevox.server.routes.validate_media_file", return_value={"duration": 5.0, "info": {}}),
        patch("vibevox.server.routes.convert_to_wav", return_value="/tmp/fake.wav"),
        patch("vibevox.server.routes._get_transcriber", return_value=mock_transcriber),
        patch("pathlib.Path.unlink"),
    ):
        r = client.post(
            "/transcribe",
            data={"format": "txt", "diarization": "true"},
            files={"file": ("test.wav", b"fake-wav", "audio/wav")},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["format"] == "txt"
    assert data["duration_seconds"] == 5.0
    assert "transcript" in data
    assert data["segments"] == MOCK_SEGMENTS


def test_transcribe_inference_error(client):
    mock_transcriber = MagicMock()
    mock_transcriber.transcribe.side_effect = RuntimeError("OOM")

    with (
        patch("vibevox.server.routes.validate_media_file", return_value={"duration": 5.0, "info": {}}),
        patch("vibevox.server.routes.convert_to_wav", return_value="/tmp/fake.wav"),
        patch("vibevox.server.routes._get_transcriber", return_value=mock_transcriber),
        patch("pathlib.Path.unlink"),
    ):
        r = client.post(
            "/transcribe",
            files={"file": ("test.wav", b"fake-wav", "audio/wav")},
        )

    assert r.status_code == 500
    assert "OOM" in r.json()["detail"]
