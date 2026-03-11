import io
import tempfile
from pathlib import Path

import streamlit as st

from vibevox.core.converter import convert_to_wav
from vibevox.core.formatters import format_all_as_zip, format_segments
from vibevox.core.transcriber import DEFAULT_MODEL, Transcriber
from vibevox.core.validator import ValidationError, validate_media_file

st.set_page_config(page_title="vibevox", page_icon="🎙", layout="centered")
st.title("vibevox")
st.caption("Audio & video transcription powered by Microsoft VibeVoice ASR")

# ── Options ─────────────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "Upload audio or video file (max 60 min)",
    type=["wav", "mp3", "flac", "ogg", "opus", "webm", "m4a", "mp4", "mkv", "avi", "mov"],
)

col1, col2, col3 = st.columns(3)

with col1:
    language = st.selectbox(
        "Language",
        options=["auto", "en", "fr", "de", "es", "it", "pt", "nl", "zh", "ja", "ko", "ar", "ru"],
        index=0,
    )

with col2:
    fmt = st.selectbox(
        "Output format",
        options=["txt", "srt", "vtt", "json", "all"],
        index=0,
    )

with col3:
    diarization = st.toggle("Speaker diarization", value=True)

model = st.text_input("Model", value=DEFAULT_MODEL, help="HuggingFace model ID — downloaded automatically if not cached")

transcribe_btn = st.button("Transcribe", type="primary", disabled=uploaded is None)

# ── Pipeline ────────────────────────────────────────────────────────────────

if transcribe_btn and uploaded is not None:
    suffix = Path(uploaded.name).suffix or ".bin"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    tmp_wav = None
    try:
        with st.spinner("Validating file…"):
            try:
                file_info = validate_media_file(tmp_path)
            except ValidationError as e:
                st.error(str(e))
                st.stop()

        duration = file_info["duration"]

        with st.spinner("Converting audio…"):
            try:
                wav_path = convert_to_wav(tmp_path)
                if wav_path != tmp_path:
                    tmp_wav = wav_path
            except RuntimeError as e:
                st.error(str(e))
                st.stop()

        with st.spinner(f"Transcribing with {model}…"):
            try:
                transcriber = Transcriber(model_id=model, device="auto")
                segments = transcriber.transcribe(
                    wav_path,
                    language=None if language == "auto" else language,
                    diarization=diarization,
                )
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

        stem = Path(uploaded.name).stem
        metadata = {
            "duration_seconds": duration,
            "model": model,
            "language": language,
        }

        st.success(f"Done — {duration:.1f}s of audio transcribed")

        if fmt == "all":
            zip_bytes = format_all_as_zip(
                segments, stem=stem, diarization=diarization, metadata=metadata
            )
            st.download_button(
                label="Download all formats (.zip)",
                data=zip_bytes,
                file_name=f"{stem}.zip",
                mime="application/zip",
            )
        else:
            content = format_segments(
                segments, fmt=fmt, diarization=diarization, metadata=metadata
            )
            st.text_area("Transcript", value=content, height=400)
            st.download_button(
                label=f"Download .{fmt}",
                data=content.encode("utf-8"),
                file_name=f"{stem}.{fmt}",
                mime="text/plain",
            )

    finally:
        Path(tmp_path).unlink(missing_ok=True)
        if tmp_wav and Path(tmp_wav).exists():
            Path(tmp_wav).unlink(missing_ok=True)
