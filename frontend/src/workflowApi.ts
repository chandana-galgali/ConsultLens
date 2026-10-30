import { configureApi } from "./api";
const base = import.meta.env.VITE_API_URL ?? "";
let token = "";
export interface Staff { id: number; email: string; role: "admin" | "doctor" | "nurse" | "lab"; }
export function setSession(value: string) { token = value; configureApi(base, value); }
async function request<T>(path: string, method: string, body?: unknown): Promise<T> {
  const response = await fetch(`${base}${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => null) as {detail?: string} | null;
    throw new Error(error?.detail || `${method} ${path}: ${response.status}`);
  }
  return response.json() as Promise<T>;
}
export async function login(email: string, password: string): Promise<Staff> {
  const response = await fetch(`${base}/auth/login`, {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email,password}),
  });
  if (!response.ok) throw new Error("Sign in failed. Check your credentials.");
  const session = await response.json() as {access_token:string;user:Staff};
  setSession(session.access_token);
  return session.user;
}
export const saveNote = (pid:number, language:string, transcript:string, reviewed_text:string) =>
  request<{id:number}>(`/workflow/patients/${pid}/notes`, "POST", {language, transcript, reviewed_text});
export const listNotes = (pid:number) => request<{id:number;language:string;reviewed_text:string}[]>(`/workflow/patients/${pid}/notes`, "GET");
export const scheduleReminder = (pid:number, scheduled_for:string, language:string) =>
  request<{id:number;status:string;notice:string}>(`/workflow/patients/${pid}/reminders`, "POST", {scheduled_for, language});
export const updateCommunication = (pid:number, phone:string, preferred_language:string, reminder_opt_in:boolean) =>
  request(`/patients/${pid}`, "PATCH", {phone, preferred_language, reminder_opt_in});

export const createStaff = (email:string,password:string,role:Staff["role"]) =>
  request<Staff>("/auth/staff", "POST", {email,password,role});

export interface EvidenceReview { id:number; patient_id:number; target_type:"observation"|"checklist"; target_id:string; decision:string; reason:string; reviewer:string; document_id:number|null; created_at:string; before:Record<string,unknown>|null; after:Record<string,unknown>|null; }
export interface ReviewObservation {id:number;label:string;code:string;value_num:number|null;value_text:string|null;unit:string|null; observed_on:string|null;snippet:string|null;document_id:number|null;filename:string|null;verified:boolean;review:EvidenceReview|null;}
export interface ReviewChecklist {id:string;label:string;status:string;review:EvidenceReview|null;}
export interface ReviewQueue {observations:ReviewObservation[];checklist:ReviewChecklist[];history:EvidenceReview[];disclaimer:string;}
export type ReviewDecision = "verified"|"corrected"|"unavailable"|"clarification"|"reviewed";
export const getReviewQueue = (pid:number) => request<ReviewQueue>(`/reviews/patients/${pid}`,"GET");
export const submitReview = (pid:number, body:{target_type:"observation"|"checklist";target_id:string;decision:ReviewDecision;reason:string;corrected_value_num?:number;corrected_value_text?:string;}) => request<EvidenceReview>(`/reviews/patients/${pid}`,"POST",body);

export async function transcribeAudio(file:File,language:string,syntheticConsent:boolean):Promise<{transcript:string;language:string;status:string}>{
  const form=new FormData();form.append("file",file);form.append("language",language);form.append("synthetic_consent",String(syntheticConsent));
  const response=await fetch(`${base}/workflow/transcribe`,{method:"POST",headers:{Authorization:`Bearer ${token}`},body:form});
  if(!response.ok){const data=await response.json().catch(()=>null) as {detail?:string}|null;throw new Error(data?.detail||`Transcription failed (${response.status})`);}
  return response.json() as Promise<{transcript:string;language:string;status:string}>;
}
