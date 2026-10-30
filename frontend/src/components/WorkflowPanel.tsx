import {useEffect, useState} from "react";
import {listNotes, saveNote, scheduleReminder, updateCommunication, transcribeAudio, type Staff} from "../workflowApi";

type Lang = "en" | "hi" | "mr";
const langs: Record<Lang,string> = {en:"English",hi:"हिन्दी",mr:"मराठी"};
interface SpeechResult { results: ArrayLike<ArrayLike<{transcript:string}>>; resultIndex:number; }
interface SpeechSession { lang:string; continuous:boolean; interimResults:boolean; onresult:((e:SpeechResult)=>void)|null; onerror:((e:{error:string})=>void)|null; start():void;stop():void; }
type SpeechCtor = new()=>SpeechSession;
interface SpeechWindow extends Window { SpeechRecognition?:SpeechCtor; webkitSpeechRecognition?:SpeechCtor; }
export default function WorkflowPanel({patientId, user}: {patientId:number;user:Staff}) {
  const [lang,setLang]=useState<Lang>("en");
  const [transcript,setTranscript]=useState("");
  const [reviewed,setReviewed]=useState("");
  const [notes,setNotes]=useState<{id:number;language:string;reviewed_text:string}[]>([]);
  const [date,setDate]=useState("");
  const [audioFile,setAudioFile]=useState<File|null>(null);
  const [audioConsent,setAudioConsent]=useState(false);
  const [phone,setPhone]=useState("");
  const [consent,setConsent]=useState(false);
  const [message,setMessage]=useState("");
  const [busy,setBusy]=useState(false);
  useEffect(()=>{setTranscript("");setReviewed("");listNotes(patientId).then(setNotes).catch(()=>setNotes([]));},[patientId]);
  const canWrite=user.role==="doctor" || user.role==="nurse";
  function record() {
    const w=window as SpeechWindow;
    const Ctor=w.SpeechRecognition??w.webkitSpeechRecognition;
    if(!Ctor){setMessage("Speech recognition is unavailable in this browser. Type or paste a transcript instead.");return;}
    const rec=new Ctor();rec.lang=lang==="en"?"en-IN":lang==="hi"?"hi-IN":"mr-IN";
    rec.continuous=false;rec.interimResults=false;
    rec.onresult=(ev)=>{const text=Array.from(ev.results).map(r=>r[0]?.transcript??"").join(" ");setTranscript(v=>[v,text].filter(Boolean).join(" "));setReviewed(v=>[v,text].filter(Boolean).join(" "));};
    rec.onerror=ev=>setMessage(`Speech capture: ${ev.error}. You can enter text manually.`);
    try {rec.start();setMessage("Listening… speech will be inserted as a draft for human review.");}catch{setMessage("Microphone could not be started.");}
  }
  async function transcribeUpload(){if(!audioFile)return;setBusy(true);setMessage("");try{const out=await transcribeAudio(audioFile,lang,audioConsent);setTranscript(out.transcript);setReviewed(out.transcript);setMessage("AI transcription prepared as draft. Review all text before saving.");}catch(e){setMessage(String(e));}finally{setBusy(false);}}
  async function approve(){setBusy(true);setMessage("");try{await saveNote(patientId,lang,transcript,reviewed);setNotes(await listNotes(patientId));setTranscript("");setReviewed("");setMessage("Reviewed note saved with an audit event.");}catch(e){setMessage(String(e));}finally{setBusy(false);}}
  async function consentSave(){setBusy(true);try{await updateCommunication(patientId,phone,lang,consent);setMessage("Contact preferences saved.");}catch(e){setMessage(String(e));}finally{setBusy(false);}}
  async function remind(){setBusy(true);try{if(!date)throw new Error("Choose appointment date and time");const result=await scheduleReminder(patientId,new Date(date).toISOString(),lang);setMessage(`${result.status}: ${result.notice}`);}catch(e){setMessage(String(e));}finally{setBusy(false);}}
  return <section className="workflow-panel" aria-label="Consultation workflow">
    <header><h2>VoiceBridge & Care Coordination</h2><p>Human-reviewed documentation · Multilingual workflow · Synthetic/demo communications</p></header>
    <label>Working language <select value={lang} onChange={e=>setLang(e.target.value as Lang)}>{Object.entries(langs).map(([code,label])=><option key={code} value={code}>{label}</option>)}</select></label>
    {canWrite && <div className="workflow-grid"><div className="workflow-card"><h3>Consultation dictation</h3><p>Speech transcription uses the browser service when available. Review every word before saving; this is not an automatic translation or clinical note generator.</p><button type="button" onClick={record}>🎙 Start browser dictation</button>
    <div className="audio-upload"><label>Or upload recorded synthetic audio (AI transcription, optional)<input type="file" accept="audio/*,.mp4,.m4a" onChange={e=>setAudioFile(e.target.files?.[0]??null)}/></label>
    <label className="consent"><input type="checkbox" checked={audioConsent} onChange={e=>setAudioConsent(e.target.checked)}/> I confirm this recording contains only synthetic, consented demo content</label>
    <button type="button" disabled={busy||!audioFile||!audioConsent} onClick={()=>void transcribeUpload()}>Transcribe recording to draft</button></div><label>Transcript<textarea rows={4} value={transcript} onChange={e=>{setTranscript(e.target.value);setReviewed(e.target.value);}} placeholder="Dictate or paste the original-language transcript"/></label><label>Clinician-approved note<textarea rows={4} value={reviewed} onChange={e=>setReviewed(e.target.value)} placeholder="Correct and approve the final text"/></label><button disabled={busy||!transcript.trim()||!reviewed.trim()} onClick={approve}>Save approved note</button></div>
    <div className="workflow-card"><h3>Patient contact & reminders</h3><p>Explicit consent is required. Messages are queued in mock mode; they are never silently sent to real patients.</p><label>Phone (+country code)<input value={phone} onChange={e=>setPhone(e.target.value)} placeholder="+919876543210"/></label><label className="consent"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/> Patient opted in to appointment reminders</label><button disabled={busy} onClick={consentSave}>Save contact preferences</button><label>Appointment date/time<input type="datetime-local" value={date} onChange={e=>setDate(e.target.value)}/></label><button disabled={busy} onClick={remind}>Queue test reminder</button></div></div>}
    <div className="workflow-card"><h3>Approved notes</h3>{notes.length?notes.map(n=><p key={n.id}><strong>#{n.id} · {langs[n.language as Lang]??n.language}</strong> — {n.reviewed_text}</p>):<p>No approved notes yet.</p>}</div>
    {message&&<p role="status" className="workflow-message">{message}</p>}
  </section>;
}
