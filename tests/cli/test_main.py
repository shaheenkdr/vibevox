import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from vibevox.cli.main import app

runner = CliRunner()


def test_transcribe_outputs_txt_to_stdout(tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"fake")
    with patch("vibevox.cli.main.validate_media_file", return_value={"duration": 5.0}), \
         patch("vibevox.cli.main.convert_to_wav", return_value=str(audio)), \
         patch("vibevox.cli.main.Transcriber") as MockT:
        MockT.return_value.transcribe.return_value = [
            {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello world."}
        ]
        result = runner.invoke(app, ["transcribe", str(audio)])
    assert result.exit_code == 0
    assert "Hello world." in result.output


def test_transcribe_invalid_format_exits_nonzero(tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"fake")
    result = runner.invoke(app, ["transcribe", str(audio), "-f", "docx"])
    assert result.exit_code != 0


def test_transcribe_writes_output_file(tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"fake")
    out = tmp_path / "output.srt"
    with patch("vibevox.cli.main.validate_media_file", return_value={"duration": 5.0}), \
         patch("vibevox.cli.main.convert_to_wav", return_value=str(audio)), \
         patch("vibevox.cli.main.Transcriber") as MockT:
        MockT.return_value.transcribe.return_value = [
            {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello."}
        ]
        result = runner.invoke(app, ["transcribe", str(audio), "-f", "srt", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "00:00:00,000" in out.read_text()


def test_transcribe_validation_error_shows_message(tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"fake")
    from vibevox.core.validator import ValidationError
    with patch("vibevox.cli.main.validate_media_file", side_effect=ValidationError("Not a valid media file")):
        result = runner.invoke(app, ["transcribe", str(audio)])
    assert result.exit_code != 0
    assert "Not a valid media file" in result.output


def test_transcribe_all_format_writes_zip(tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"fake")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    with patch("vibevox.cli.main.validate_media_file", return_value={"duration": 5.0}), \
         patch("vibevox.cli.main.convert_to_wav", return_value=str(audio)), \
         patch("vibevox.cli.main.Transcriber") as MockT:
        MockT.return_value.transcribe.return_value = [
            {"Start": 0.0, "End": 5.0, "Speaker": 0, "Content": "Hello."}
        ]
        result = runner.invoke(app, ["transcribe", str(audio), "-f", "all", "-o", str(out_dir)])
    assert result.exit_code == 0
    zip_files = list(out_dir.glob("*.zip"))
    assert len(zip_files) == 1
