from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import Base, ensure_columns, engine
from .routers import briefing, demo, documents, observations, patients, system, whatsapp

Base.metadata.create_all(bind=engine)
ensure_columns()

app = FastAPI(title="ConsultLens API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
for r in (patients, documents, observations, briefing, demo, whatsapp, system):
    app.include_router(r.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# One-command deploy: after `npm run build` in frontend/, the API also serves the built UI at http://localhost:8000
_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="ui")
