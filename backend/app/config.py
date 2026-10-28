from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str = ""
    bootstrap_email: str = ""
    bootstrap_password: str = ""
    message_provider: str = "mock"
    max_upload_mb: int = 12
    database_url: str = "sqlite:///./consultlens.db"
    upload_dir: str = "./uploads"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Shown in the app header / printed briefing
    clinic_name: str = "Demo Women's Clinic"
    clinician_name: str = "Dr. A. Rao (demo)"

    # OCR
    tesseract_cmd: str | None = None      # e.g. C:\Program Files\Tesseract-OCR\tesseract.exe (auto-detected if left empty)
    poppler_path: str | None = None       # Windows only, folder containing pdftoppm.exe (needed for scanned PDFs)
    use_textract: bool = False
    aws_region: str = "ap-south-1"

    # Optional: Claude wording of the summary (never interprets)
    anthropic_api_key: str | None = None
    claude_model: str = "claude-sonnet-5-5"

    # Optional: WhatsApp (Twilio) ingestion
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None

    # Optional: CARE EMR link (placeholder, used by the Care plugin / adapter)
    care_base_url: str | None = None
    care_token: str | None = None


settings = Settings()
