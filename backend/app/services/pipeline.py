from sqlalchemy.orm import Session

from .. import models
from . import extraction, ocr
from .timeline_builder import ga_weeks


def store_observations(db: Session, doc: models.Document) -> None:
    """(Re)build the observations of a document from its stored text.
    Values a clinician edited or confirmed are kept when the same line is extracted again."""
    patient = doc.patient
    previous = {(o.code, o.snippet): o for o in db.query(models.Observation).filter_by(document_id=doc.id).all()}
    db.query(models.Observation).filter_by(document_id=doc.id).delete()

    for o in extraction.extract_observations(doc.ocr_text or "", doc.doc_date, doc.doc_type):
        old = previous.get((o.code, o.snippet))
        value_num, value_text, edited, verified = o.value_num, o.value_text, 0, 0
        if old is not None:
            verified, edited = int(old.verified or 0), int(old.edited or 0)
            if edited:
                value_num, value_text = old.value_num, old.value_text
        db.add(models.Observation(
            patient_id=patient.id, document_id=doc.id, code=o.code, label=o.label,
            value_num=value_num, value_text=value_text, unit=o.unit,
            observed_on=o.observed_on, gestation_weeks=ga_weeks(patient.lmp, o.observed_on),
            snippet=o.snippet, verified=verified, edited=edited,
        ))
    db.commit()


def process_document(db: Session, doc: models.Document, user_date=None, text_override: str | None = None) -> models.Document:
    """OCR -> classify -> date -> observations -> save.
    text_override is only used by the demo seeder when OCR is not installed (the engine is then labelled clearly)."""
    if text_override is not None:
        text, engine, conf = text_override, "demo-text (OCR unavailable)", None
    else:
        text, engine, conf = ocr.extract_text(doc.stored_path)
    doc.ocr_text, doc.ocr_engine, doc.ocr_confidence = text, engine, conf
    doc.doc_type = extraction.classify(text)
    doc.doc_date = user_date or extraction.find_doc_date(text)
    db.commit()
    store_observations(db, doc)
    db.refresh(doc)
    return doc


def reextract_document(db: Session, doc: models.Document) -> models.Document:
    """Re-run extraction from the stored text (no OCR). Used after a clinician changes a document's type or date."""
    store_observations(db, doc)
    db.refresh(doc)
    return doc


def reprocess_patient(db: Session, patient: models.Patient) -> None:
    """Re-derive gestation weeks after the patient's LMP changes."""
    for doc in list(patient.documents):
        reextract_document(db, doc)
