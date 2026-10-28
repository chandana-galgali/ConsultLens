import {useState} from "react";
import {login,type Staff} from "../workflowApi";
export default function Login({onLogin}:{onLogin:(user:Staff)=>void}){
 const[email,setEmail]=useState("");const[password,setPassword]=useState("");const[error,setError]=useState("");const[busy,setBusy]=useState(false);
 return <main className="login-screen"><form className="login-card" onSubmit={async e=>{e.preventDefault();setBusy(true);setError("");try{onLogin(await login(email,password));}catch(err){setError(String(err));}finally{setBusy(false);}}}>
 <div className="login-brand">✚ Consult<span>Lens</span></div><h1>Clinical workspace</h1><p>Secure staff access · Demo and synthetic data only</p>
 <label>Email<input type="email" autoComplete="username" required value={email} onChange={e=>setEmail(e.target.value)}/></label>
 <label>Password<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)}/></label>
 {error&&<p role="alert" className="workflow-message">{error}</p>}<button disabled={busy} type="submit">{busy?"Signing in…":"Sign in"}</button>
 </form></main>;
}
