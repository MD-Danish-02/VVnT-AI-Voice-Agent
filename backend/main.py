from fastapi import FastAPI

app = FastAPI(
    title="VVnT AI Voice Agent",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "vvnt-ai-voice-agent",
    }