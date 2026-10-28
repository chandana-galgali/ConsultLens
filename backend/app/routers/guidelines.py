"""Provenance metadata for reference guidance; not clinical decision rules."""
from fastapi import APIRouter

router = APIRouter(prefix="/references", tags=["guideline references"])
@router.get("/antenatal")
def antenatal_references():
    return {"clinical_rule_status": "not validated for clinical use",
            "references": [
                {"publisher":"WHO", "title":"WHO recommendations on antenatal care for a positive pregnancy experience",
                 "year":2016,"url":"https://www.who.int/publications/i/item/9789241549912",
                 "scope":"Global routine ANC; includes eight-contact model; context adaptation required",
                 "status":"reference only"},
                {"publisher":"FOGSI / ICOG", "title":"Routine Antenatal Care for the Healthy Pregnant Women",
                 "year":2024,"url":"https://www.fogsi.org/wp-content/uploads/2024/08/Binder_Routine-Antenatal-Care-for-the-Healthy-Pregnant-Women.pdf",
                 "scope":"India-focused routine ANC reference; detailed recommendations pending clinician approval",
                 "status":"reference only"},
            ]}
