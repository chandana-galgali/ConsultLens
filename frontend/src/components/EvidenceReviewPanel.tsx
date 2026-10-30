import {useCallback,useEffect,useState} from "react";
import {openDoc} from "../api";
import {getReviewQueue,submitReview,type ReviewQueue,type ReviewDecision,type Staff} from "../workflowApi";

type Target = {type:"observation"|"checklist";id:string;label:string;value?:string;};
export default function EvidenceReviewPanel({patientId,user,onUpdated}:{patientId:number;user:Staff;onUpdated:()=>void}) {
  const [queue,setQueue]=useState<ReviewQueue|null>(null);
  const [error,setError]=useState("");
  const [target,setTarget]=useState<Target|null>(null);
  const [decision,setDecision]=useState<ReviewDecision>("verified");
  const [reason,setReason]=useState("");
  const [corrected,setCorrected]=useState("");
  const [busy,setBusy]=useState(false);
  const refresh=useCallback(()=>getReviewQueue(patientId).then(data=>{setQueue(data);setError("");}).catch(e=>setError(String(e))),[patientId]);
  useEffect(()=>{setQueue(null);setTarget(null);void refresh();},[refresh]);
  const canEdit=user.role!=="admin";
  function choose(item:Target, initial:ReviewDecision){setTarget(item);setDecision(initial);setReason("");setCorrected(item.value??"");setError("");}
  async function save(){
    if(!target||reason.trim().length<3){setError("Enter a review explanation of at least three characters.");return;}
    setBusy(true);setError("");
    try {
      const body:{target_type:"observation"|"checklist";target_id:string;decision:ReviewDecision;reason:string;corrected_value_num?:number;corrected_value_text?:string}={target_type:target.type,target_id:target.id,decision,reason:reason.trim()};
      if(decision==="corrected"){
        if(!corrected.trim()){throw new Error("Enter the corrected value.");}
        if(target.value!==undefined && /^-?\d+(?:\.\d+)?$/.test(corrected.trim())) body.corrected_value_num=Number(corrected);
        else body.corrected_value_text=corrected.trim();
      }
      await submitReview(patientId,body);setTarget(null);await refresh();onUpdated();
    }catch(e){setError(e instanceof Error?e.message:String(e));}finally{setBusy(false);}
  }
  if(!queue)return <section className="review-panel"><h2>Evidence review queue</h2><p role="status">{error||"Loading source records…"}</p></section>;
  const obsPending=queue.observations.filter(o=>!o.review||o.review.decision==="clarification").length;
  const checklistPending=queue.checklist.filter(c=>!c.review).length;
  return <section className="review-panel" aria-label="Evidence review queue">
    <div className="review-heading"><div><h2>Evidence review queue</h2><p>Review extracted facts and document availability. All decisions record the reviewer, reason and time.</p></div><button className="btn btn-outline" onClick={()=>void refresh()}>Refresh queue</button></div>
    <div className="review-statline"><span>{obsPending} facts awaiting review</span><span>{checklistPending} checklist items without review</span><span>{queue.history.length} recent actions</span></div>
    <p className="review-disclaimer">{queue.disclaimer} “Not found” means not found in the available documents; it does not establish that a test was never performed.</p>
    {error&&<p role="alert" className="review-error">{error}</p>}
    {target&&<div className="review-editor" role="region" aria-label="Record decision">
      <h3>{target.label}</h3><p>Review item: {target.type} #{target.id}</p>
      <label>Decision<select value={decision} onChange={e=>setDecision(e.target.value as ReviewDecision)}>
        {target.type==="observation"&&<><option value="verified">Verified against source</option><option value="corrected">Correct extracted value</option></>}
        <option value="clarification">Request clarification</option><option value="unavailable">Not available in supplied records</option>
        <option value="reviewed">Reviewed, no change</option>
      </select></label>
      {decision==="corrected"&&<label>Correct value<input aria-label="Corrected value" value={corrected} onChange={e=>setCorrected(e.target.value)}/></label>}
      <label>Reviewer explanation<textarea rows={3} value={reason} onChange={e=>setReason(e.target.value)} placeholder="Record what you checked and why…"/></label>
      <div className="review-actions"><button disabled={busy||reason.trim().length<3} onClick={()=>void save()} className="btn btn-primary">{busy?"Saving…":"Save reviewed decision"}</button><button disabled={busy} className="btn btn-outline" onClick={()=>setTarget(null)}>Cancel</button></div>
    </div>}
    <h3>Extracted facts <small>({queue.observations.length})</small></h3>
    {queue.observations.length===0?<p className="review-empty">No extracted observations yet. Upload a sample lab or visit document to populate this queue.</p>:<div className="review-list">{queue.observations.map(o=><article className="review-item" key={o.id}>
      <div className="review-item-main"><strong>{o.label}</strong><span className="review-value">{o.value_num??o.value_text??"Unspecified"} {o.unit??""}</span><span className="review-muted">{o.observed_on??"Date unknown"} · {o.filename??"Manual entry"}</span>
      {o.snippet&&<blockquote className="review-snippet">{o.snippet}</blockquote>}
      <span className="review-state">{o.review?`${o.review.decision} · ${o.review.reviewer}`:(o.verified?"Previously verified":"Awaiting review")}</span></div>
      <div className="review-actions">{o.document_id!=null&&<button className="btn btn-outline" onClick={()=>void openDoc(o.document_id!)}>Open source</button>}{canEdit&&<button className="btn btn-primary" onClick={()=>choose({type:"observation",id:String(o.id),label:o.label,value:String(o.value_num??o.value_text??"")},"verified")}>Review fact</button>}</div>
    </article>)}</div>}
    <h3>Documentation checklist <small>({queue.checklist.length})</small></h3>
    <div className="review-list">{queue.checklist.map(c=><article className="review-item" key={c.id}><div className="review-item-main"><strong>{c.label}</strong><span className="review-muted">Automated status: {c.status.replaceAll("_"," ")}</span><span className="review-state">{c.review?`${c.review.decision} · ${c.review.reviewer}`:"Not manually reviewed"}</span></div>{canEdit&&user.role!=="lab"&&<button className="btn btn-outline" onClick={()=>choose({type:"checklist",id:c.id,label:c.label},"reviewed")}>Review item</button>}</article>)}</div>
    <h3>Review history</h3>{queue.history.length===0?<p className="review-empty">No decisions have been recorded for this patient.</p>:<div className="review-list">{queue.history.map(h=><div key={h.id} className="review-history"><strong>{h.decision}</strong> · {h.target_type} #{h.target_id} · {h.reviewer}<p>{h.reason}</p><small>{new Date(h.created_at).toLocaleString()}</small></div>)}</div>}
  </section>;
}
