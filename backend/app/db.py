from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = "postgresql+psycopg://" + db_url[len("postgres://"):]
elif db_url.startswith("postgresql://"):
    db_url = "postgresql+psycopg://" + db_url[len("postgresql://"):]
engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Columns added after v1. create_all() never alters existing tables, so we add them here.
# This keeps an older consultlens.db working without deleting it.
_NEW_COLUMNS = {
    "patients": {"profile": "TEXT", "preferred_language": "VARCHAR(16) DEFAULT 'en'", "reminder_opt_in": "INTEGER DEFAULT 0"},
    "documents": {"ocr_confidence": "FLOAT"},
    "observations": {"verified": "INTEGER DEFAULT 0", "edited": "INTEGER DEFAULT 0"},
}


def ensure_columns() -> None:
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, cols in _NEW_COLUMNS.items():
            if not insp.has_table(table):
                continue
            have = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in cols.items():
                if name not in have:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
