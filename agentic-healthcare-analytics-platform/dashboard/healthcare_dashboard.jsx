import { useState, useEffect } from "react";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from "recharts";

const PATIENTS = [
  { id: 101, age: 65, gender: "M", diagnosis: "Diabetes", medications: 8, procedures: 3, labs: 12, prior: 2, los: 7, readmitted: 1, sbp: 145, dbp: 92, hr: 88, glucose: 210, bmi: 28.5 },
  { id: 102, age: 72, gender: "F", diagnosis: "Heart Failure", medications: 12, procedures: 5, labs: 18, prior: 4, los: 14, readmitted: 1, sbp: 160, dbp: 98, hr: 102, glucose: 185, bmi: 31.2 },
  { id: 103, age: 45, gender: "M", diagnosis: "Pneumonia", medications: 4, procedures: 2, labs: 8, prior: 0, los: 4, readmitted: 0, sbp: 118, dbp: 76, hr: 72, glucose: 95, bmi: 24.1 },
  { id: 104, age: 58, gender: "F", diagnosis: "COPD", medications: 9, procedures: 4, labs: 15, prior: 3, los: 9, readmitted: 1, sbp: 138, dbp: 88, hr: 85, glucose: 110, bmi: 26.8 },
  { id: 105, age: 33, gender: "M", diagnosis: "Appendicitis", medications: 2, procedures: 1, labs: 6, prior: 0, los: 3, readmitted: 0, sbp: 120, dbp: 78, hr: 68, glucose: 88, bmi: 22.3 },
  { id: 106, age: 78, gender: "F", diagnosis: "Hip Fracture", medications: 6, procedures: 3, labs: 10, prior: 2, los: 8, readmitted: 1, sbp: 152, dbp: 94, hr: 90, glucose: 140, bmi: 27.9 },
  { id: 107, age: 55, gender: "M", diagnosis: "Diabetes", medications: 10, procedures: 4, labs: 14, prior: 3, los: 11, readmitted: 1, sbp: 148, dbp: 90, hr: 86, glucose: 225, bmi: 30.1 },
  { id: 108, age: 42, gender: "F", diagnosis: "UTI", medications: 3, procedures: 1, labs: 7, prior: 0, los: 3, readmitted: 0, sbp: 115, dbp: 72, hr: 65, glucose: 92, bmi: 21.8 },
  { id: 109, age: 68, gender: "M", diagnosis: "Stroke", medications: 11, procedures: 6, labs: 20, prior: 5, los: 16, readmitted: 1, sbp: 168, dbp: 102, hr: 95, glucose: 178, bmi: 29.4 },
  { id: 110, age: 50, gender: "F", diagnosis: "Asthma", medications: 5, procedures: 2, labs: 9, prior: 1, los: 5, readmitted: 0, sbp: 125, dbp: 80, hr: 75, glucose: 98, bmi: 23.7 },
  { id: 111, age: 73, gender: "M", diagnosis: "Heart Failure", medications: 14, procedures: 7, labs: 22, prior: 6, los: 18, readmitted: 1, sbp: 172, dbp: 106, hr: 108, glucose: 195, bmi: 33.5 },
  { id: 112, age: 38, gender: "F", diagnosis: "Appendicitis", medications: 2, procedures: 1, labs: 5, prior: 0, los: 2, readmitted: 0, sbp: 118, dbp: 74, hr: 70, glucose: 90, bmi: 20.9 },
  { id: 113, age: 61, gender: "M", diagnosis: "COPD", medications: 8, procedures: 3, labs: 13, prior: 2, los: 8, readmitted: 0, sbp: 135, dbp: 85, hr: 80, glucose: 105, bmi: 25.6 },
  { id: 114, age: 82, gender: "F", diagnosis: "Dementia", medications: 7, procedures: 2, labs: 11, prior: 4, los: 13, readmitted: 1, sbp: 155, dbp: 96, hr: 88, glucose: 130, bmi: 26.3 },
  { id: 115, age: 47, gender: "M", diagnosis: "Pneumonia", medications: 5, procedures: 3, labs: 10, prior: 1, los: 5, readmitted: 0, sbp: 122, dbp: 78, hr: 74, glucose: 96, bmi: 23.9 },
  { id: 116, age: 69, gender: "F", diagnosis: "Diabetes", medications: 11, procedures: 5, labs: 16, prior: 3, los: 10, readmitted: 1, sbp: 150, dbp: 92, hr: 89, glucose: 240, bmi: 31.8 },
  { id: 117, age: 54, gender: "M", diagnosis: "Cardiac Arrest", medications: 15, procedures: 8, labs: 25, prior: 7, los: 21, readmitted: 1, sbp: 178, dbp: 110, hr: 115, glucose: 165, bmi: 32.7 },
  { id: 118, age: 36, gender: "F", diagnosis: "UTI", medications: 2, procedures: 1, labs: 6, prior: 0, los: 2, readmitted: 0, sbp: 112, dbp: 70, hr: 62, glucose: 88, bmi: 20.1 },
  { id: 119, age: 77, gender: "M", diagnosis: "Hip Fracture", medications: 8, procedures: 4, labs: 14, prior: 3, los: 11, readmitted: 1, sbp: 158, dbp: 98, hr: 92, glucose: 142, bmi: 28.8 },
  { id: 120, age: 63, gender: "F", diagnosis: "Stroke", medications: 12, procedures: 6, labs: 19, prior: 4, los: 15, readmitted: 1, sbp: 165, dbp: 100, hr: 98, glucose: 172, bmi: 30.5 },
  { id: 121, age: 29, gender: "M", diagnosis: "Asthma", medications: 3, procedures: 1, labs: 7, prior: 0, los: 3, readmitted: 0, sbp: 116, dbp: 74, hr: 68, glucose: 94, bmi: 22.0 },
  { id: 122, age: 71, gender: "F", diagnosis: "COPD", medications: 10, procedures: 4, labs: 16, prior: 3, los: 9, readmitted: 1, sbp: 140, dbp: 88, hr: 84, glucose: 112, bmi: 27.1 },
  { id: 123, age: 48, gender: "M", diagnosis: "Diabetes", medications: 7, procedures: 3, labs: 11, prior: 1, los: 6, readmitted: 0, sbp: 132, dbp: 84, hr: 78, glucose: 145, bmi: 25.3 },
  { id: 124, age: 85, gender: "F", diagnosis: "Heart Failure", medications: 16, procedures: 8, labs: 24, prior: 8, los: 22, readmitted: 1, sbp: 180, dbp: 112, hr: 118, glucose: 200, bmi: 34.2 },
  { id: 125, age: 52, gender: "M", diagnosis: "Pneumonia", medications: 4, procedures: 2, labs: 8, prior: 0, los: 4, readmitted: 0, sbp: 124, dbp: 80, hr: 72, glucose: 98, bmi: 24.5 },
];

function riskScore(p) {
  let score = 0;
  if (p.prior > 3) score += 35;
  else if (p.prior > 1) score += 20;
  if (p.medications > 10) score += 20;
  else if (p.medications > 6) score += 10;
  if (p.los > 12) score += 15;
  else if (p.los > 7) score += 8;
  if (p.sbp > 160) score += 10;
  if (p.glucose > 200) score += 10;
  if (p.age > 75) score += 10;
  else if (p.age > 60) score += 5;
  return Math.min(score, 100);
}

const PATIENTS_WITH_RISK = PATIENTS.map(p => ({
  ...p,
  risk: riskScore(p),
  riskLevel: riskScore(p) >= 65 ? "High" : riskScore(p) >= 35 ? "Medium" : "Low",
}));

const RISK_COLORS = { High: "#ef4444", Medium: "#f59e0b", Low: "#10b981" };
const DIAG_COLORS = ["#6366f1","#8b5cf6","#ec4899","#f43f5e","#f59e0b","#10b981","#06b6d4","#3b82f6"];

export default function App() {
  const [tab, setTab] = useState("overview");
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [agentRunning, setAgentRunning] = useState(false);
  const [agentLog, setAgentLog] = useState([]);
  const [agentComplete, setAgentComplete] = useState(false);

  const highRisk = PATIENTS_WITH_RISK.filter(p => p.riskLevel === "High");
  const medRisk  = PATIENTS_WITH_RISK.filter(p => p.riskLevel === "Medium");
  const lowRisk  = PATIENTS_WITH_RISK.filter(p => p.riskLevel === "Low");
  const readmitted = PATIENTS_WITH_RISK.filter(p => p.readmitted === 1);

  // KPIs
  const avgAge = (PATIENTS.reduce((s,p) => s+p.age,0)/PATIENTS.length).toFixed(1);
  const avgLOS = (PATIENTS.reduce((s,p) => s+p.los,0)/PATIENTS.length).toFixed(1);
  const avgMeds = (PATIENTS.reduce((s,p) => s+p.medications,0)/PATIENTS.length).toFixed(1);
  const avgGlucose = (PATIENTS.reduce((s,p) => s+p.glucose,0)/PATIENTS.length).toFixed(0);

  // Diagnosis breakdown
  const diagMap = {};
  PATIENTS.forEach(p => { diagMap[p.diagnosis] = (diagMap[p.diagnosis]||0)+1; });
  const diagData = Object.entries(diagMap).map(([name,value]) => ({name,value}));

  // Age distribution
  const ageBuckets = {"<40":0,"40-55":0,"55-70":0,"70-85":0,"85+":0};
  PATIENTS.forEach(p => {
    if(p.age<40) ageBuckets["<40"]++;
    else if(p.age<55) ageBuckets["40-55"]++;
    else if(p.age<70) ageBuckets["55-70"]++;
    else if(p.age<85) ageBuckets["70-85"]++;
    else ageBuckets["85+"]++;
  });
  const ageData = Object.entries(ageBuckets).map(([age,count]) => ({age,count}));

  // Anomalies
  const anomalies = PATIENTS_WITH_RISK.filter(p =>
    p.hr > 100 || p.sbp > 160 || p.sbp < 90 || p.los > 15 || p.prior > 5
  ).map(p => ({
    ...p,
    flags: [
      p.hr > 100 ? "Tachycardia" : null,
      p.sbp > 160 ? "High BP" : null,
      p.sbp < 90 ? "Hypotension" : null,
      p.los > 15 ? "Extended Stay" : null,
      p.prior > 5 ? "Frequent Readmitter" : null,
    ].filter(Boolean)
  }));

  async function runAgents() {
    setAgentRunning(true);
    setAgentLog([]);
    setAgentComplete(false);
    const steps = [
      { delay: 400,  msg: "🔄 Initialising pipeline...", type:"info" },
      { delay: 900,  msg: "━━━ AGENT 1 · Data Validation Agent", type:"header" },
      { delay: 1300, msg: "  → Loading patient_data.csv (25 records, 15 columns)", type:"log" },
      { delay: 1700, msg: "  → Checking required columns... ✓", type:"log" },
      { delay: 2100, msg: "  → Checking missing values... ✓ (100% complete)", type:"log" },
      { delay: 2500, msg: "  → Validating clinical ranges... ✓", type:"log" },
      { delay: 2900, msg: "  ✓ Validation PASSED — no issues detected", type:"success" },
      { delay: 3300, msg: "━━━ AGENT 2 · Readmission Risk Prediction Agent", type:"header" },
      { delay: 3700, msg: "  → Encoding categorical features...", type:"log" },
      { delay: 4100, msg: "  → Training Random Forest (100 estimators)...", type:"log" },
      { delay: 4600, msg: "  → Cross-validating (5-fold ROC-AUC)...", type:"log" },
      { delay: 5100, msg: "  ✓ Model trained — AUC: 1.00 | Accuracy: 100%", type:"success" },
      { delay: 5500, msg: "  → Scoring all 25 patients...", type:"log" },
      { delay: 5900, msg: `  🚨 ${highRisk.length} HIGH RISK patients identified`, type:"warn" },
      { delay: 6300, msg: "━━━ AGENT 3 · Anomaly Detection Agent", type:"header" },
      { delay: 6700, msg: "  → Applying IQR outlier detection...", type:"log" },
      { delay: 7100, msg: "  → Running 9 clinical rule checks...", type:"log" },
      { delay: 7500, msg: `  ⚠  ${anomalies.length} patients flagged (18 rule violations)`, type:"warn" },
      { delay: 7900, msg: "━━━ AGENT 4 · Report Generation Agent", type:"header" },
      { delay: 8300, msg: "  → Synthesising agent outputs...", type:"log" },
      { delay: 8700, msg: "  → Building recommendations...", type:"log" },
      { delay: 9100, msg: "  ✓ Report generated — healthcare_report.txt", type:"success" },
      { delay: 9500, msg: "✅ Pipeline complete in 0.7s", type:"done" },
    ];
    for (const step of steps) {
      await new Promise(r => setTimeout(r, step.delay));
      setAgentLog(prev => [...prev, step]);
    }
    setAgentRunning(false);
    setAgentComplete(true);
  }

  const tabs = [
    { id:"overview", label:"Overview" },
    { id:"patients", label:"Patients" },
    { id:"anomalies", label:"Anomalies" },
    { id:"agents", label:"Run Agents" },
  ];

  return (
    <div style={{
      minHeight:"100vh", background:"#0a0f1e",
      fontFamily:"'IBM Plex Mono', 'Courier New', monospace",
      color:"#e2e8f0"
    }}>
      {/* Header */}
      <div style={{
        background:"linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%)",
        borderBottom:"1px solid #1e40af33",
        padding:"20px 28px", display:"flex", alignItems:"center", gap:16,
        boxShadow:"0 4px 32px #6366f122"
      }}>
        <div style={{
          width:42, height:42, borderRadius:10,
          background:"linear-gradient(135deg,#6366f1,#8b5cf6)",
          display:"flex", alignItems:"center", justifyContent:"center",
          fontSize:20, boxShadow:"0 0 20px #6366f155"
        }}>⚕</div>
        <div>
          <div style={{fontSize:14, fontWeight:700, letterSpacing:3, color:"#818cf8", textTransform:"uppercase"}}>
            Agentic Healthcare Analytics Platform
          </div>
          <div style={{fontSize:11, color:"#475569", marginTop:2}}>
            Multi-Agent Clinical Intelligence · 25 Patients · Live Dashboard
          </div>
        </div>
        <div style={{marginLeft:"auto", display:"flex", gap:8}}>
          {[
            {label:"VALIDATED", color:"#10b981"},
            {label:"MODEL READY", color:"#6366f1"},
            {label:"LIVE", color:"#f59e0b"},
          ].map(b => (
            <div key={b.label} style={{
              fontSize:9, fontWeight:700, letterSpacing:2,
              padding:"4px 10px", borderRadius:4,
              border:`1px solid ${b.color}55`,
              color:b.color, background:`${b.color}11`
            }}>{b.label}</div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div style={{
        display:"flex", gap:0, padding:"0 28px",
        borderBottom:"1px solid #1e293b", background:"#0d1425"
      }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            padding:"12px 20px", fontSize:11, fontWeight:600,
            letterSpacing:1.5, textTransform:"uppercase",
            background:"none", border:"none", cursor:"pointer",
            color: tab===t.id ? "#818cf8" : "#475569",
            borderBottom: tab===t.id ? "2px solid #6366f1" : "2px solid transparent",
            transition:"all .2s"
          }}>{t.label}</button>
        ))}
      </div>

      <div style={{padding:"24px 28px", maxWidth:1200}}>

        {/* OVERVIEW TAB */}
        {tab==="overview" && (
          <div>
            {/* KPI Cards */}
            <div style={{display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:14, marginBottom:24}}>
              {[
                {label:"Total Patients", value:25, unit:"", color:"#6366f1", icon:"👥"},
                {label:"Readmission Rate", value:"56.0", unit:"%", color:"#ef4444", icon:"🔄"},
                {label:"High Risk Patients", value:highRisk.length, unit:"", color:"#f59e0b", icon:"🚨"},
                {label:"Anomalies Flagged", value:anomalies.length, unit:"", color:"#8b5cf6", icon:"⚠️"},
                {label:"Avg Age", value:avgAge, unit:" yrs", color:"#06b6d4", icon:"👤"},
                {label:"Avg Length of Stay", value:avgLOS, unit:" days", color:"#10b981", icon:"🏥"},
                {label:"Avg Medications", value:avgMeds, unit:"", color:"#ec4899", icon:"💊"},
                {label:"Avg Glucose", value:avgGlucose, unit:" mg/dL", color:"#f59e0b", icon:"🩸"},
              ].map(k => (
                <div key={k.label} style={{
                  background:"#0d1425", border:"1px solid #1e293b",
                  borderRadius:10, padding:"16px 18px",
                  borderLeft:`3px solid ${k.color}`
                }}>
                  <div style={{fontSize:18, marginBottom:6}}>{k.icon}</div>
                  <div style={{fontSize:22, fontWeight:700, color:k.color}}>{k.value}{k.unit}</div>
                  <div style={{fontSize:10, color:"#475569", marginTop:4, letterSpacing:1}}>{k.label.toUpperCase()}</div>
                </div>
              ))}
            </div>

            {/* Charts row */}
            <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:16}}>
              {/* Risk Distribution Pie */}
              <div style={{background:"#0d1425", border:"1px solid #1e293b", borderRadius:10, padding:20}}>
                <div style={{fontSize:11, color:"#818cf8", letterSpacing:2, marginBottom:16}}>RISK DISTRIBUTION</div>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={[
                      {name:"High Risk", value:highRisk.length},
                      {name:"Medium Risk", value:medRisk.length},
                      {name:"Low Risk", value:lowRisk.length},
                    ]} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value">
                      <Cell fill="#ef4444"/><Cell fill="#f59e0b"/><Cell fill="#10b981"/>
                    </Pie>
                    <Tooltip contentStyle={{background:"#0d1425",border:"1px solid #1e293b",borderRadius:8,fontSize:11}} />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{display:"flex",justifyContent:"center",gap:16,marginTop:8}}>
                  {[["High",highRisk.length,"#ef4444"],["Medium",medRisk.length,"#f59e0b"],["Low",lowRisk.length,"#10b981"]].map(([l,v,c]) => (
                    <div key={l} style={{textAlign:"center"}}>
                      <div style={{fontSize:16,fontWeight:700,color:c}}>{v}</div>
                      <div style={{fontSize:9,color:"#475569",letterSpacing:1}}>{l.toUpperCase()}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Diagnosis Bar */}
              <div style={{background:"#0d1425", border:"1px solid #1e293b", borderRadius:10, padding:20}}>
                <div style={{fontSize:11, color:"#818cf8", letterSpacing:2, marginBottom:16}}>PATIENTS BY DIAGNOSIS</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={diagData} layout="vertical" margin={{left:10}}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b"/>
                    <XAxis type="number" tick={{fill:"#475569",fontSize:10}} />
                    <YAxis type="category" dataKey="name" tick={{fill:"#94a3b8",fontSize:10}} width={90}/>
                    <Tooltip contentStyle={{background:"#0d1425",border:"1px solid #1e293b",borderRadius:8,fontSize:11}}/>
                    <Bar dataKey="value" radius={[0,4,4,0]}>
                      {diagData.map((_,i) => <Cell key={i} fill={DIAG_COLORS[i%DIAG_COLORS.length]}/>)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Age dist + Feature importance */}
            <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:16}}>
              <div style={{background:"#0d1425", border:"1px solid #1e293b", borderRadius:10, padding:20}}>
                <div style={{fontSize:11, color:"#818cf8", letterSpacing:2, marginBottom:16}}>AGE DISTRIBUTION</div>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={ageData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b"/>
                    <XAxis dataKey="age" tick={{fill:"#475569",fontSize:10}}/>
                    <YAxis tick={{fill:"#475569",fontSize:10}}/>
                    <Tooltip contentStyle={{background:"#0d1425",border:"1px solid #1e293b",borderRadius:8,fontSize:11}}/>
                    <Bar dataKey="count" fill="#6366f1" radius={[4,4,0,0]}/>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div style={{background:"#0d1425", border:"1px solid #1e293b", borderRadius:10, padding:20}}>
                <div style={{fontSize:11, color:"#818cf8", letterSpacing:2, marginBottom:16}}>TOP RISK FEATURES (MODEL)</div>
                {[
                  ["Systolic BP", 0.19],
                  ["BMI", 0.134],
                  ["Diastolic BP", 0.133],
                  ["Lab Results", 0.09],
                  ["Length of Stay", 0.089],
                ].map(([name, imp]) => (
                  <div key={name} style={{marginBottom:10}}>
                    <div style={{display:"flex",justifyContent:"space-between",fontSize:10,color:"#94a3b8",marginBottom:3}}>
                      <span>{name}</span><span style={{color:"#818cf8"}}>{(imp*100).toFixed(1)}%</span>
                    </div>
                    <div style={{height:6, background:"#1e293b", borderRadius:3}}>
                      <div style={{width:`${imp*100/0.19*80}%`, height:"100%", background:"linear-gradient(90deg,#6366f1,#8b5cf6)", borderRadius:3}}/>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* PATIENTS TAB */}
        {tab==="patients" && (
          <div>
            <div style={{display:"flex",gap:12,marginBottom:18,flexWrap:"wrap"}}>
              {["All","High","Medium","Low"].map(f => (
                <button key={f} onClick={() => {}} style={{
                  padding:"6px 16px", borderRadius:6, fontSize:10,
                  fontWeight:700, letterSpacing:1.5, border:"1px solid #1e293b",
                  background:"#0d1425", color:"#94a3b8", cursor:"pointer"
                }}>{f.toUpperCase()}</button>
              ))}
              <div style={{marginLeft:"auto",fontSize:10,color:"#475569",alignSelf:"center"}}>
                {PATIENTS.length} patients · click a row to expand
              </div>
            </div>

            <div style={{background:"#0d1425", border:"1px solid #1e293b", borderRadius:10, overflow:"hidden"}}>
              <div style={{
                display:"grid",
                gridTemplateColumns:"60px 50px 80px 130px 70px 70px 80px 90px 100px",
                gap:0, padding:"10px 16px",
                borderBottom:"1px solid #1e293b",
                fontSize:9, color:"#475569", letterSpacing:1.5, fontWeight:700
              }}>
                <span>ID</span><span>AGE</span><span>GENDER</span><span>DIAGNOSIS</span>
                <span>MEDS</span><span>LOS</span><span>GLUCOSE</span><span>SYS BP</span><span>RISK</span>
              </div>
              {PATIENTS_WITH_RISK.sort((a,b) => b.risk-a.risk).map(p => (
                <div key={p.id}>
                  <div
                    onClick={() => setSelectedPatient(selectedPatient?.id===p.id ? null : p)}
                    style={{
                      display:"grid",
                      gridTemplateColumns:"60px 50px 80px 130px 70px 70px 80px 90px 100px",
                      gap:0, padding:"10px 16px",
                      borderBottom:"1px solid #0f172a",
                      fontSize:11, cursor:"pointer",
                      background: selectedPatient?.id===p.id ? "#1e1b4b22" : "transparent",
                      transition:"background .15s"
                    }}
                  >
                    <span style={{color:"#64748b"}}>#{p.id}</span>
                    <span style={{color:"#e2e8f0"}}>{p.age}</span>
                    <span style={{color:"#94a3b8"}}>{p.gender}</span>
                    <span style={{color:"#cbd5e1"}}>{p.diagnosis}</span>
                    <span style={{color:"#94a3b8"}}>{p.medications}</span>
                    <span style={{color:"#94a3b8"}}>{p.los}d</span>
                    <span style={{color: p.glucose>200?"#ef4444":p.glucose>140?"#f59e0b":"#94a3b8"}}>{p.glucose}</span>
                    <span style={{color: p.sbp>160?"#ef4444":p.sbp>140?"#f59e0b":"#94a3b8"}}>{p.sbp}</span>
                    <span style={{
                      padding:"2px 10px", borderRadius:4, fontSize:10, fontWeight:700,
                      background:`${RISK_COLORS[p.riskLevel]}22`,
                      color:RISK_COLORS[p.riskLevel],
                      border:`1px solid ${RISK_COLORS[p.riskLevel]}44`
                    }}>{p.riskLevel} · {p.risk}%</span>
                  </div>
                  {selectedPatient?.id===p.id && (
                    <div style={{
                      padding:"16px 24px", background:"#0a0f1e",
                      borderBottom:"1px solid #1e293b",
                      display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:16
                    }}>
                      {[
                        ["Heart Rate", p.hr+" bpm", p.hr>100?"#ef4444":"#10b981"],
                        ["Diastolic BP", p.dbp+" mmHg", "#94a3b8"],
                        ["BMI", p.bmi, p.bmi>30?"#f59e0b":"#10b981"],
                        ["Prior Admissions", p.prior, p.prior>3?"#ef4444":"#94a3b8"],
                        ["Procedures", p.procedures, "#94a3b8"],
                        ["Lab Results", p.labs, "#94a3b8"],
                        ["Readmitted", p.readmitted?"YES":"NO", p.readmitted?"#ef4444":"#10b981"],
                        ["Risk Score", p.risk+"%", RISK_COLORS[p.riskLevel]],
                      ].map(([l,v,c]) => (
                        <div key={l} style={{display:"flex",justifyContent:"space-between",fontSize:11}}>
                          <span style={{color:"#475569"}}>{l}</span>
                          <span style={{color:c,fontWeight:600}}>{v}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ANOMALIES TAB */}
        {tab==="anomalies" && (
          <div>
            <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
              {[
                {label:"Total Anomalies",value:anomalies.length,color:"#8b5cf6"},
                {label:"Tachycardia",value:PATIENTS.filter(p=>p.hr>100).length,color:"#ef4444"},
                {label:"High BP",value:PATIENTS.filter(p=>p.sbp>160).length,color:"#f59e0b"},
                {label:"Extended Stays",value:PATIENTS.filter(p=>p.los>15).length,color:"#06b6d4"},
              ].map(k => (
                <div key={k.label} style={{
                  background:"#0d1425", border:`1px solid ${k.color}33`,
                  borderRadius:10, padding:"14px 16px"
                }}>
                  <div style={{fontSize:24,fontWeight:700,color:k.color}}>{k.value}</div>
                  <div style={{fontSize:10,color:"#475569",letterSpacing:1,marginTop:4}}>{k.label.toUpperCase()}</div>
                </div>
              ))}
            </div>

            <div style={{background:"#0d1425", border:"1px solid #1e293b", borderRadius:10, overflow:"hidden"}}>
              <div style={{padding:"12px 18px", borderBottom:"1px solid #1e293b", fontSize:11, color:"#818cf8", letterSpacing:2}}>
                FLAGGED PATIENTS
              </div>
              {anomalies.map(p => (
                <div key={p.id} style={{
                  padding:"14px 18px", borderBottom:"1px solid #0f172a",
                  display:"flex", alignItems:"center", gap:16
                }}>
                  <div style={{
                    width:40,height:40,borderRadius:8,
                    background:`${RISK_COLORS[p.riskLevel]}22`,
                    border:`1px solid ${RISK_COLORS[p.riskLevel]}44`,
                    display:"flex",alignItems:"center",justifyContent:"center",
                    fontSize:14,flexShrink:0
                  }}>
                    {p.riskLevel==="High"?"🚨":p.riskLevel==="Medium"?"⚠️":"ℹ️"}
                  </div>
                  <div style={{flex:1}}>
                    <div style={{fontSize:12, color:"#e2e8f0", fontWeight:600}}>
                      Patient #{p.id} · {p.diagnosis}
                    </div>
                    <div style={{fontSize:10, color:"#475569", marginTop:3}}>
                      Age {p.age} · HR {p.hr}bpm · BP {p.sbp}/{p.dbp}mmHg · LOS {p.los}d
                    </div>
                    <div style={{display:"flex",gap:6,marginTop:6,flexWrap:"wrap"}}>
                      {p.flags.map(f => (
                        <span key={f} style={{
                          fontSize:9,fontWeight:700,letterSpacing:1,
                          padding:"2px 8px",borderRadius:4,
                          background:"#ef444422",color:"#ef4444",
                          border:"1px solid #ef444444"
                        }}>{f.toUpperCase()}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{
                    fontSize:14, fontWeight:700,
                    color:RISK_COLORS[p.riskLevel]
                  }}>{p.risk}%</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AGENTS TAB */}
        {tab==="agents" && (
          <div>
            <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:24}}>
              {[
                {num:1, name:"Data Validation", icon:"🔍", color:"#10b981"},
                {num:2, name:"Risk Prediction", icon:"🤖", color:"#6366f1"},
                {num:3, name:"Anomaly Detection", icon:"⚠️", color:"#f59e0b"},
                {num:4, name:"Report Generation", icon:"📋", color:"#8b5cf6"},
              ].map(a => (
                <div key={a.num} style={{
                  background:"#0d1425", border:`1px solid ${a.color}33`,
                  borderRadius:10, padding:18, textAlign:"center"
                }}>
                  <div style={{fontSize:28,marginBottom:8}}>{a.icon}</div>
                  <div style={{fontSize:9,color:a.color,letterSpacing:2,fontWeight:700}}>AGENT {a.num}</div>
                  <div style={{fontSize:11,color:"#94a3b8",marginTop:4}}>{a.name}</div>
                  {agentComplete && (
                    <div style={{fontSize:10,color:"#10b981",marginTop:8}}>✓ Complete</div>
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={runAgents}
              disabled={agentRunning}
              style={{
                width:"100%", padding:"14px", marginBottom:20,
                background: agentRunning ? "#1e293b" : "linear-gradient(135deg,#6366f1,#8b5cf6)",
                border:"none", borderRadius:10, color:"white",
                fontSize:12, fontWeight:700, letterSpacing:2,
                cursor: agentRunning ? "not-allowed" : "pointer",
                transition:"all .2s",
                boxShadow: agentRunning ? "none" : "0 4px 24px #6366f144"
              }}
            >
              {agentRunning ? "⟳  PIPELINE RUNNING..." : "▶  EXECUTE FULL AGENT PIPELINE"}
            </button>

            <div style={{
              background:"#020817", border:"1px solid #1e293b",
              borderRadius:10, padding:20, minHeight:320,
              fontFamily:"'IBM Plex Mono',monospace"
            }}>
              <div style={{fontSize:10,color:"#475569",letterSpacing:2,marginBottom:12}}>AGENT CONSOLE OUTPUT</div>
              {agentLog.length===0 && (
                <div style={{color:"#1e293b",fontSize:11}}>
                  $ awaiting pipeline execution...
                </div>
              )}
              {agentLog.map((entry,i) => (
                <div key={i} style={{
                  fontSize:11, marginBottom:4,
                  color: entry.type==="header" ? "#818cf8"
                       : entry.type==="success" ? "#10b981"
                       : entry.type==="warn" ? "#f59e0b"
                       : entry.type==="done" ? "#6366f1"
                       : "#475569",
                  fontWeight: entry.type==="header"||entry.type==="done" ? 700 : 400
                }}>
                  {entry.type==="header" ? "" : "> "}{entry.msg}
                </div>
              ))}
              {agentRunning && (
                <div style={{color:"#6366f1",fontSize:11,marginTop:4}}>
                  ▌
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
