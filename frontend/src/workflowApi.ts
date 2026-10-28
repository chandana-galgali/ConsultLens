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
