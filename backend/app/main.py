from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .security import current_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import Base, ensure_columns, engine
from .routers import briefing, demo, documents, observations, patients, system, whatsapp, auth, workflow, guidelines

Base.metadata.create_all(bind=engine)
ensure_columns()

app = FastAPI(title="ConsultLens API", version="0.3.0", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for r in (auth, workflow, guidelines, patients, documents, observations, briefing, demo, whatsapp, system):
    if r is auth:
        app.include_router(r.router)
    elif r is whatsapp:
        # Inbound public webhooks need signed validation; not mounted until reviewed.
        continue
    else:
        from fastapi import Depends
        app.include_router(r.router, dependencies=[Depends(current_user)])


@app.get("/health")
def health():
    return {"status": "ok"}


# One-command deploy: after `npm run build` in frontend/, the API also serves the built UI at http://localhost:8000
_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="ui")
