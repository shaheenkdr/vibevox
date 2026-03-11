from vibevox.core.logger import get_logger

logger = get_logger(__name__)

DEFAULT_MODEL = "microsoft/VibeVoice-ASR-HF"


class _NotAvailable:
    """Placeholder for optional imports not yet installed."""
    _name: str = "unknown"

    def __init_subclass__(cls, name: str = "unknown", **kwargs):
        super().__init_subclass__(**kwargs)
        cls._name = name

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        raise RuntimeError(
            f"{cls._name} is not available. "
            "Run: pip install torch transformers>=4.51.3"
        )


class _TorchPlaceholder(_NotAvailable, name="torch"):
    bfloat16 = None


class _AutoProcessorPlaceholder(_NotAvailable, name="AutoProcessor"):
    pass


class _VibeVoicePlaceholder(_NotAvailable, name="VibeVoiceAsrForConditionalGeneration"):
    pass


# Import at module level for patchability in tests.
try:
    import torch
except ImportError:
    torch = _TorchPlaceholder  # type: ignore

try:
    from transformers import AutoProcessor, VibeVoiceAsrForConditionalGeneration
except ImportError:
    AutoProcessor = _AutoProcessorPlaceholder  # type: ignore
    VibeVoiceAsrForConditionalGeneration = _VibeVoicePlaceholder  # type: ignore


class Transcriber:
    """
    Wraps VibeVoice ASR. Loads the model once and reuses it across calls.

    Args:
        model_id: HuggingFace model ID (default: microsoft/VibeVoice-ASR-HF).
                  Downloaded automatically on first use and cached in
                  ~/.cache/huggingface/hub/.
        device:   "auto" (default), "cpu", or "cuda".
        chunk_size: acoustic_tokenizer_chunk_size for memory tuning.
                    Default None uses the model's built-in default (60 min @ 24kHz).
    """

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL,
        device: str = "auto",
        chunk_size: int = None,
    ):
        self.model_id = model_id
        self.device = device
        self.chunk_size = chunk_size
        self._processor = None
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        logger.info(f"Loading model: {self.model_id}")
        self._processor = AutoProcessor.from_pretrained(self.model_id)
        self._model = VibeVoiceAsrForConditionalGeneration.from_pretrained(
            self.model_id,
            device_map=self.device,
            torch_dtype=torch.bfloat16,
        )
        logger.info("Model loaded.")

    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        diarization: bool = True,
        decode: str = "greedy",
    ) -> list:
        """
        Transcribe a 24kHz mono WAV file.

        Returns a list of segments:
            [{"Start": float, "End": float, "Speaker": int|None, "Content": str}, ...]
        """
        self._load()

        kwargs = {}
        if language:
            kwargs["language"] = language

        inputs = self._processor.apply_transcription_request(
            audio=audio_path,
            **kwargs,
        )
        inputs = inputs.to(self._model.device, self._model.dtype)

        gen_kwargs = {}
        if self.chunk_size is not None:
            gen_kwargs["acoustic_tokenizer_chunk_size"] = self.chunk_size
        if decode == "beam":
            gen_kwargs["num_beams"] = 4

        output_ids = self._model.generate(**inputs, **gen_kwargs)
        generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]
        segments = self._processor.decode(generated_ids, return_format="parsed")[0]

        if not diarization:
            for seg in segments:
                seg["Speaker"] = None

        return segments
