from fastapi import FastAPI

app = FastAPI(
    title="Paradigm Ra Platform API",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "paradigm-ra-platform",
    }