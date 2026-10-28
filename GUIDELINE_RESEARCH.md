# Source-backed guidance research — non-clinical release

The *WHO Recommendations on Antenatal Care for a Positive Pregnancy Experience* (2016) is the most comprehensive publicly accessible global reference used in this pass. WHO's 2016 implementation chapter describes an eight-contact model at **up to 12, 20, 26, 30, 34, 36, 38, and 40 weeks**, and stresses contextual adaptation. This is contextual reference material, **not an automated schedule of appointments**. The WHO page explicitly lists subsequent topic updates. See:
- https://www.who.int/publications/i/item/9789241549912
- https://www.ncbi.nlm.nih.gov/books/NBK409109/

The India-relevant *FOGSI/ICOG Routine Antenatal Care for the Healthy Pregnant Women* (2024) was located at:
- https://www.fogsi.org/wp-content/uploads/2024/08/Binder_Routine-Antenatal-Care-for-the-Healthy-Pregnant-Women.pdf

The full FOGSI PDF was indexed publicly, but direct text retrieval returned HTTP 403 during this pass. Accordingly no detailed FOGSI decision rules were transcribed. This avoids implying verification that did not occur.

`backend/app/rules/antenatal_schedule.yaml` remains a **demonstration-only, unapproved documentation checklist** inherited from the original repository. It must not be described as implementing FOGSI, WHO, ACOG or RCOG recommendations. The improved matching code enforces the configured temporal windows, but the actual windows remain unapproved.

The hackathon feature set is therefore *source-linked record extraction, document availability, administrative workflow, and clinician-reviewed notes*, not AI diagnosis, risk scoring or treatment recommendations.
