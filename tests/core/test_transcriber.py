import pytest
from unittest.mock import patch, MagicMock
from vibevox.core.transcriber import Transcriber, DEFAULT_MODEL


def _make_mock_model_and_processor():
    processor = MagicMock()
    model = MagicMock()

    inputs = MagicMock()
    inputs.__getitem__ = lambda self, key: MagicMock()
    inputs.to.return_value = inputs
    processor.apply_transcription_request.return_value = inputs

    output_ids = MagicMock()
    model.generate.return_value = output_ids
    model.device = "cpu"
    model.dtype = "float32"

    processor.decode.return_value = [
        [
            {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello."},
            {"Start": 5.0, "End": 10.0, "Speaker": 1, "Content": "World."},
        ]
    ]
    return processor, model


@pytest.mark.slow
def test_transcriber_returns_segments():
    processor, model = _make_mock_model_and_processor()
    with patch("vibevox.core.transcriber.AutoProcessor.from_pretrained", return_value=processor), \
         patch("vibevox.core.transcriber.VibeVoiceAsrForConditionalGeneration.from_pretrained", return_value=model):
        t = Transcriber()
        segments = t.transcribe("fake_audio.wav")
    assert len(segments) == 2
    assert segments[0]["Content"] == "Hello."
    assert segments[1]["Speaker"] == 1


@pytest.mark.slow
def test_transcriber_no_diarization_nulls_speakers():
    processor, model = _make_mock_model_and_processor()
    with patch("vibevox.core.transcriber.AutoProcessor.from_pretrained", return_value=processor), \
         patch("vibevox.core.transcriber.VibeVoiceAsrForConditionalGeneration.from_pretrained", return_value=model):
        t = Transcriber()
        segments = t.transcribe("fake_audio.wav", diarization=False)
    assert all(seg["Speaker"] is None for seg in segments)


@pytest.mark.slow
def test_transcriber_model_loaded_once():
    processor, model = _make_mock_model_and_processor()
    with patch("vibevox.core.transcriber.AutoProcessor.from_pretrained", return_value=processor) as mock_proc, \
         patch("vibevox.core.transcriber.VibeVoiceAsrForConditionalGeneration.from_pretrained", return_value=model):
        t = Transcriber()
        t.transcribe("audio.wav")
        t.transcribe("audio2.wav")
    assert mock_proc.call_count == 1


def test_default_model_is_vibevoice_asr_hf():
    assert "VibeVoice-ASR-HF" in DEFAULT_MODEL
