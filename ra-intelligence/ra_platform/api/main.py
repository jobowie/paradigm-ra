from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from ra_platform.api.routes.auth import (
    router as auth_router,
)
from ra_platform.api.routes.admin_quotes import (
    router as admin_quotes_router,
)
from ra_platform.api.routes.payments import (
    router as payments_router,
)
from ra_platform.api.routes.quotes import (
    router as quotes_router,
)
from ra_platform.api.routes.admin_platform import (
    router as admin_platform_router,
)



load_dotenv()

app = FastAPI(
    title="Paradigm Ra Platform API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://paradigmra.tech",
        "https://www.paradigmra.tech",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "X-RA-Admin-Key",
    ],
)

app.include_router(
    auth_router
)

app.include_router(
    admin_platform_router
)
app.include_router(
    quotes_router
)
app.include_router(
    admin_quotes_router
)
app.include_router(
    payments_router
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "paradigm-ra-platform",
    }
