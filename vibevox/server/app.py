from fastapi import FastAPI

from vibevox.server.routes import router

app = FastAPI(
    title="vibevox",
    description="Audio and video transcription powered by Microsoft VibeVoice ASR",
    version="0.1.0",
)
app.include_router(router)
