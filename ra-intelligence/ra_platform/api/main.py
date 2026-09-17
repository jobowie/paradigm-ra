from fastapi import FastAPI

from ra_platform.api.routes.admin_quotes import (
    router as admin_quotes_router,
)
from ra_platform.api.routes.quotes import (
    router as quotes_router,
)


app = FastAPI(
    title="Paradigm Ra Platform API",
    version="0.1.0",
)

app.include_router(quotes_router)
app.include_router(admin_quotes_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "paradigm-ra-platform",
    }
