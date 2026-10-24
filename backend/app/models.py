from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(64), index=True)  # e.g. the Care patient id
    mrn: Mapped[str | None] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(32), index=True)  # used to match WhatsApp senders
    age: Mapped[int | None] = mapped_column(Integer)
    blood_group: Mapped[str | None] = mapped_column(String(8))
    lmp: Mapped[date | None] = mapped_column(Date)
    edd: Mapped[date | None] = mapped_column(Date)  # as recorded by the clinic
    gravida: Mapped[int | None] = mapped_column(Integer)
    para: Mapped[int | None] = mapped_column(Integer)
    # JSON text: history sections typed at registration (same fields as the paper antenatal record)
    profile: Mapped[str | None] = mapped_column(Text)

    documents: Mapped[list["Document"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    observations: Mapped[list["Observation"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(32), default="upload")  # upload | whatsapp | emr
    doc_type: Mapped[str] = mapped_column(String(32), default="unknown")
    doc_date: Mapped[date | None] = mapped_column(Date)
    ocr_text: Mapped[str | None] = mapped_column(Text)
    ocr_engine: Mapped[str | None] = mapped_column(String(32))
    ocr_confidence: Mapped[float | None] = mapped_column(Float)  # mean word confidence, Tesseract/Textract only
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="documents")


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"))
    code: Mapped[str] = mapped_column(String(32), index=True)  # hb, bp_sys, tt1, med, plan ...
    label: Mapped[str] = mapped_column(String(100))
    value_num: Mapped[float | None] = mapped_column(Float)
    value_text: Mapped[str | None] = mapped_column(String(200))
    unit: Mapped[str | None] = mapped_column(String(32))
    observed_on: Mapped[date | None] = mapped_column(Date)
    gestation_weeks: Mapped[float | None] = mapped_column(Float)
    snippet: Mapped[str | None] = mapped_column(String(300))  # the source text line the value came from
    verified: Mapped[int] = mapped_column(Integer, default=0)  # clinician confirmed against the original
    edited: Mapped[int] = mapped_column(Integer, default=0)    # clinician corrected the extracted value

    patient: Mapped[Patient] = relationship(back_populates="observations")
