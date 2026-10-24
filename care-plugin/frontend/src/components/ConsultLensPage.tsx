// Care plugin page. Drop the ConsultLens frontend components next to this file (see ../../PORTING_PROMPT.md):
//   src/api.ts, src/types.ts, src/components/{BriefingView,GapPanel,TrendTable,Timeline,DocLink,UploadBox,NewPatientForm}.tsx
// This wrapper is the only Care-specific piece: it receives the Care patient id and looks up (or creates) the
// linked ConsultLens record.
//
// NOT VERIFIED against a running Care instance. How to obtain the Care patient id, the Care API URL and the
// user's token must follow the conventions in the scaffold / care_ai_vision_fe (see PORTING_PROMPT.md).
import { useCallback, useEffect, useState } from "react";
import { configureApi, getBriefingByExternal } from "../api";
import type { Briefing, PatientT } from "../types";
import BriefingView from "./BriefingView";
import NewPatientForm from "./NewPatientForm";
import UploadBox from "./UploadBox";

interface Props {
  /** The Care patient id (UUID/external id). */
  patientId: string;
  patientName?: string;
  /** e.g. https://care.example.org/api/care_consultlens/v1/proxy  (the Django proxy plugin) */
  apiBaseUrl: string;
  /** Returns the logged-in Care user's auth header, e.g. { Authorization: `Bearer ${token}` } */
  getAuthHeaders: () => Record<string, string>;
}

export default function ConsultLensPage({ patientId, patientName, apiBaseUrl, getAuthHeaders }: Props) {
  const [b, setB] = useState<Briefing | null>(null);
  const [state, setState] = useState<"loading" | "missing" | "ready" | "error">("loading");
  const [err, setErr] = useState("");

  useEffect(() => {
    configureApi({ baseUrl: apiBaseUrl, headers: getAuthHeaders });
  }, [apiBaseUrl, getAuthHeaders]);

  const load = useCallback(async () => {
    try {
      setB(await getBriefingByExternal(patientId));
      setState("ready");
    } catch (x) {
      const msg = String((x as Error).message);
      if (msg.startsWith("404")) setState("missing");
      else { setErr(msg); setState("error"); }
    }
  }, [patientId]);

  useEffect(() => { load(); }, [load]);

  if (state === "loading") return <p>Loading ConsultLens briefing...</p>;
  if (state === "error") return <p className="err">ConsultLens is unavailable: {err}</p>;
  if (state === "missing")
    return <NewPatientForm externalId={patientId} defaultName={patientName} onCreated={(_p: PatientT) => load()} />;

  return (
    <div className="consultlens">
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <UploadBox patientId={b!.patient.id} onDone={load} />
      </div>
      <BriefingView b={b!} onChanged={load} />
    </div>
  );
}
