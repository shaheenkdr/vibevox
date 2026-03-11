from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from vibevox.core.converter import convert_to_wav
from vibevox.core.formatters import format_segments, format_all_as_zip
from vibevox.core.logger import configure_logging
from vibevox.core.transcriber import Transcriber, DEFAULT_MODEL
from vibevox.core.validator import ValidationError, validate_media_file

app = typer.Typer(
    help="vibevox — audio and video transcription powered by VibeVoice ASR",
    add_completion=False,
)
console = Console()

VALID_FORMATS = {"txt", "srt", "vtt", "json", "all"}


@app.command()
def transcribe(
    file: Path = typer.Argument(..., help="Audio or video file to transcribe"),
    format: str = typer.Option("txt", "-f", "--format", help="Output format: txt srt vtt json all"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file or directory (default: stdout)"),
    language: Optional[str] = typer.Option(None, "--language", help="Language code e.g. en, fr (default: auto-detect)"),
    diarization: bool = typer.Option(True, "--diarization/--no-diarization", help="Speaker diarization (default: on)"),
    decode: str = typer.Option("greedy", "--decode", help="Decoding strategy: greedy or beam"),
    device: str = typer.Option("auto", "--device", help="Device: auto cpu cuda"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="HuggingFace model ID (downloaded if not cached)"),
    chunk_size: Optional[int] = typer.Option(None, "--chunk-size", help="acoustic_tokenizer_chunk_size for memory tuning"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable debug logging"),
):
    """Transcribe an audio or video file."""
    if verbose:
        configure_logging("DEBUG")

    if format not in VALID_FORMATS:
        console.print(f"[red]Error:[/red] Invalid format {format!r}. Choose from: {', '.join(sorted(VALID_FORMATS))}")
        raise typer.Exit(code=1)

    try:
        file_info = validate_media_file(str(file))
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    duration = file_info["duration"]
    tmp_wav = None

    try:
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True, console=console) as progress:
            progress.add_task("Converting audio...")
            wav_path = convert_to_wav(str(file))
            if wav_path != str(file):
                tmp_wav = wav_path

        transcriber = Transcriber(model_id=model, device=device, chunk_size=chunk_size)
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True, console=console) as progress:
            progress.add_task(f"Transcribing with {model}...")
            segments = transcriber.transcribe(
                wav_path,
                language=language,
                diarization=diarization,
                decode=decode,
            )

        metadata = {"duration_seconds": duration, "model": model, "language": language or "auto"}
        stem = Path(file).stem

        if format == "all":
            zip_bytes = format_all_as_zip(segments, stem=stem, diarization=diarization, metadata=metadata)
            if output:
                out_dir = Path(output)
                out_dir.mkdir(parents=True, exist_ok=True)
                zip_path = out_dir / f"{stem}.zip"
            else:
                zip_path = Path(f"{stem}.zip")
            zip_path.write_bytes(zip_bytes)
            console.print(f"[green]✓[/green] Saved: {zip_path}")
        else:
            content = format_segments(segments, fmt=format, diarization=diarization, metadata=metadata)
            if output:
                out_path = Path(output)
                if out_path.is_dir():
                    out_path = out_path / f"{stem}.{format}"
                out_path.write_text(content, encoding="utf-8")
                console.print(f"[green]✓[/green] Saved: {out_path}")
            else:
                print(content)

    finally:
        if tmp_wav and Path(tmp_wav).exists():
            Path(tmp_wav).unlink(missing_ok=True)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
):
    """Start the vibevox FastAPI server."""
    try:
        import uvicorn
        from vibevox.server.app import app as fastapi_app
    except ImportError:
        console.print("[red]Error:[/red] Server dependencies not installed. Run: pip install vibevox[server]")
        raise typer.Exit(code=1)
    uvicorn.run(fastapi_app, host=host, port=port)


@app.command()
def ui(
    port: int = typer.Option(8501, "--port", help="Port for Streamlit UI"),
):
    """Launch the vibevox Streamlit UI."""
    try:
        import streamlit  # noqa: F401
    except ImportError:
        console.print("[red]Error:[/red] UI dependencies not installed. Run: pip install vibevox[ui]")
        raise typer.Exit(code=1)
    import subprocess
    ui_path = Path(__file__).parent.parent / "ui" / "app.py"
    subprocess.run(["streamlit", "run", str(ui_path), "--server.port", str(port)])
