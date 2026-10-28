import {useState} from "react";
import {createStaff,type Staff} from "../workflowApi";
export default function StaffPanel(){
 const [email,setEmail]=useState("");const[password,setPassword]=useState("");const[role,setRole]=useState<Staff["role"]>("nurse");const[msg,setMsg]=useState("");
 return <details className="staff-panel"><summary>Manage team accounts</summary><form onSubmit={async e=>{e.preventDefault();try{const result=await createStaff(email,password,role);setMsg(`Created ${result.email} (${result.role})`);setEmail("");setPassword("");}catch(err){setMsg(String(err));}}}>
 <label>Staff email<input type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label>
 <label>Initial password (12+ characters)<input type="password" minLength={12} required value={password} onChange={e=>setPassword(e.target.value)}/></label>
 <label>Role<select value={role} onChange={e=>setRole(e.target.value as Staff["role"])}><option value="doctor">Doctor</option><option value="nurse">Nurse</option><option value="lab">Lab staff</option><option value="admin">Administrator</option></select></label>
 <button type="submit">Create staff account</button><p role="status">{msg}</p></form></details>;
}
