# Prompt for Claude Code: embed ConsultLens in Care

Use this AFTER the standalone ConsultLens app works. It is meant to be pasted into Claude Code (or any coding agent)
running inside a clone of `https://github.com/ohcnetwork/care_scaffold`.

## One-time workspace setup (the scaffold does the heavy lifting)

```bash
git clone https://github.com/ohcnetwork/care_scaffold.git
cd care_scaffold
# open Claude Code here, then send exactly:
#   Read and execute ./bootstrap.prompt.md
```
Per the scaffold README, that prompt clones `care` and `care_fe`, allocates ports, starts isolated Docker services,
creates plugin repos and registers them through external config (without editing Care core).
When it asks for the plugin brief, use the text below. Needs Git, Node/npm, Python 3, Docker + Compose.

## The brief to give the agent

> Create a Care plugin named `consultlens` (backend `care_consultlens`, frontend `care_consultlens_fe`).
>
> **Goal:** a "ConsultLens" view on the patient page that shows a pre-consultation briefing: chronological patient
> journey, previous-vs-latest values, expected items not found in uploaded records, and record-quality flags.
> It only retrieves and organises data - no clinical interpretation.
>
> **Backend:** copy `care-plugin/backend/care_consultlens/` from my ConsultLens repo (a thin authenticated proxy to my
> FastAPI service, URL from config `CONSULTLENS_API_URL`). Keep secrets server-side. Add the same facility-level
> permission gate that `care_filly` uses. Add a test that disallowed routes return 403.
>
> **Frontend:** copy my React components (`frontend/src/{api.ts,types.ts,components/*}`) into the plugin and use
> `care-plugin/frontend/src/components/ConsultLensPage.tsx` as the page. Follow the conventions of the scaffold template
> and `care_ai_vision_fe` for: the manifest, routes, how to obtain the current patient id, the Care API base URL and the
> logged-in user's auth header (pass them to `ConsultLensPage` as props), and the correct extension point for a
> patient-page tab/button (check `care_fe/src/pluginTypes.ts`). Use shared deps from the host (react, react-query...).
>
> **Constraints:** zero changes to Care core; synthetic data only; do not send secrets to third parties; report anything
> unsupported as a blocker instead of patching core. Verify end to end: open a patient in Care, see the ConsultLens
> view, upload a report, see the briefing update.

## What is verified vs not

| Item | Status |
|---|---|
| Manifest shape (`plugin`, `routes`, `extends`, `components`, `userNavItems`, `devices`) | Copied from care_ai_vision_fe |
| Backend plugin registration (`plug_config.py`, mounted under `/api/<plugin-name>/`) | From Care docs + care_filly README |
| Route object format, patient-page slot name, how to get patient id/token | NOT verified - the agent must read the scaffold / care_fe |
| `views.py` proxy and `ConsultLensPage.tsx` | Written against standard Django REST / React; never run inside Care |

## If Care setup eats your time
Keep the standalone app as the demo and show a slide of where it plugs into Care. Say so honestly.
