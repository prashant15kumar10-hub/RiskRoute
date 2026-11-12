import React, { useEffect, useMemo, useState } from "react"
import {
  Activity,
  Award,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Gauge,
  History,
  LogOut,
  PackageCheck,
  Route,
  ShieldCheck,
  Sparkles,
  Truck,
  Users,
  XCircle,
} from "lucide-react"

const defaultShipment = {
  distance_km: 277,
  vehicle_load_pct: 80,
  departure_hour: 18,
  traffic_level: 2,
  weather_severity: 0,
  driver_experience_years: 3.5,
  priority_shipment: 0,
  buffer_minutes: 45,
  target_probability: 0.4,
}

async function request(path, options = {}, token = "") {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.detail || "Request failed")
  return body
}

function Auth({ onSuccess }) {
  const [register, setRegister] = useState(false)
  const [form, setForm] = useState({ name: "", email: "", password: "" })
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError("")
    try {
      const data = await request(register ? "/api/register" : "/api/login", {
        method: "POST",
        body: JSON.stringify(form),
      })
      onSuccess(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-visual">
        <div className="brand"><Truck size={26} /> RiskRoute</div>
        <div className="auth-message">
          <span>INTELLIGENT LOGISTICS</span>
          <h1>Don’t just predict delay.<br />Show what can change it.</h1>
          <p>Constraint-aware counterfactual simulation for actionable decisions.</p>
        </div>
      </section>
      <section className="auth-panel">
        <form className="auth-card" onSubmit={submit}>
          <div className="auth-icon"><Route size={25} /></div>
          <h2>{register ? "Create your workspace" : "Welcome back"}</h2>
          <p>{register ? "Start recording shipment decisions." : "Sign in to continue to the simulator."}</p>
          {register && (
            <label>Name<input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></label>
          )}
          <label>Email<input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input required minLength="6" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} /></label>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={busy}>{busy ? "Please wait…" : register ? "Create account" : "Sign in"} <ArrowRight size={18} /></button>
          <button type="button" className="link-button" onClick={() => { setRegister(!register); setError("") }}>
            {register ? "Already have an account? Sign in" : "New here? Create an account"}
          </button>
        </form>
      </section>
    </main>
  )
}

function Field({ label, children, value, suffix }) {
  return <label className="field"><span>{label}<b>{value}{suffix}</b></span>{children}</label>
}

function Simulator({ token, onSaved }) {
  const [shipment, setShipment] = useState(defaultShipment)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  function update(name, value) {
    setShipment(previous => ({ ...previous, [name]: Number(value) }))
  }

  async function simulate(event) {
    event.preventDefault()
    setBusy(true)
    setError("")
    try {
      const data = await request("/api/predict", {
        method: "POST",
        body: JSON.stringify(shipment),
      }, token)
      setResult(data)
      onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="workspace-grid">
      <form className="panel form-panel" onSubmit={simulate}>
        <div className="panel-heading"><div><span>SHIPMENT INPUT</span><h2>Operating conditions</h2></div><Truck /></div>
        <div className="fields-grid">
          <Field label="Distance" value={shipment.distance_km} suffix=" km"><input type="range" min="20" max="800" value={shipment.distance_km} onChange={e => update("distance_km", e.target.value)} /></Field>
          <Field label="Vehicle load" value={shipment.vehicle_load_pct} suffix="%"><input type="range" min="25" max="100" value={shipment.vehicle_load_pct} onChange={e => update("vehicle_load_pct", e.target.value)} /></Field>
          <Field label="Departure" value={shipment.departure_hour} suffix=":00"><input type="range" min="0" max="23" value={shipment.departure_hour} onChange={e => update("departure_hour", e.target.value)} /></Field>
          <Field label="Buffer" value={shipment.buffer_minutes} suffix=" min"><input type="range" min="0" max="120" step="5" value={shipment.buffer_minutes} onChange={e => update("buffer_minutes", e.target.value)} /></Field>
          <label className="field"><span>Traffic level</span><select value={shipment.traffic_level} onChange={e => update("traffic_level", e.target.value)}><option value="0">Clear</option><option value="1">Light</option><option value="2">Heavy</option><option value="3">Severe</option></select></label>
          <label className="field"><span>Weather severity</span><select value={shipment.weather_severity} onChange={e => update("weather_severity", e.target.value)}><option value="0">Clear</option><option value="1">Moderate</option><option value="2">Poor</option><option value="3">Severe</option></select></label>
          <Field label="Driver experience" value={shipment.driver_experience_years} suffix=" years"><input type="range" min="0" max="18" step=".5" value={shipment.driver_experience_years} onChange={e => update("driver_experience_years", e.target.value)} /></Field>
          <label className="field"><span>Priority shipment</span><select value={shipment.priority_shipment} onChange={e => update("priority_shipment", e.target.value)}><option value="0">Standard</option><option value="1">Priority</option></select></label>
        </div>
        <Field label="Target maximum risk" value={Math.round(shipment.target_probability * 100)} suffix="%"><input type="range" min=".15" max=".5" step=".05" value={shipment.target_probability} onChange={e => update("target_probability", e.target.value)} /></Field>
        {error && <div className="error">{error}</div>}
        <button className="primary simulate" disabled={busy}><Sparkles size={18} /> {busy ? "Simulating…" : "Run what-if simulation"}</button>
      </form>

      <section className="panel result-panel">
        <div className="panel-heading"><div><span>DECISION OUTPUT</span><h2>Recommended intervention</h2></div><Activity /></div>
        {!result ? (
          <div className="empty-result"><Route size={46} /><h3>Ready to simulate</h3><p>Enter shipment conditions to calculate delay risk and feasible actions.</p></div>
        ) : (
          <>
            <div className={`risk-card ${result.risk_label.toLowerCase()}`}>
              <div><span>Predicted delay risk</span><strong>{Math.round(result.delay_probability * 100)}%</strong></div>
              <div className="risk-label">{result.risk_label} risk</div>
            </div>
            <div className="scenario-title"><h3>Feasible scenarios</h3><span>Target ≤ {Math.round(result.target_probability * 100)}%</span></div>
            <div className="scenarios">
              {result.scenarios.length === 0 && <div className="no-scenario">No allowed action reaches this target. Try a higher threshold.</div>}
              {result.scenarios.map((scenario, index) => (
                <article className="scenario" key={index}>
                  <div className="scenario-number">{String(index + 1).padStart(2, "0")}</div>
                  <div className="scenario-main">
                    <div><b>{Math.round(scenario.delay_probability * 100)}% risk</b><small>Cost {scenario.cost.toFixed(2)}</small></div>
                    <div className="change-list">
                      {Object.entries(scenario.changes).map(([name, change]) => (
                        <span key={name}>{name.replaceAll("_", " ")}: {change.from} → {change.to}</span>
                      ))}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  )
}

function HistoryView({ token, refreshKey }) {
  const [history, setHistory] = useState([])
  useEffect(() => {
    request("/api/history", {}, token).then(setHistory).catch(() => setHistory([]))
  }, [token, refreshKey])
  return (
    <section className="panel history-panel">
      <div className="panel-heading"><div><span>DECISION LOG</span><h2>Simulation history</h2></div><History /></div>
      <div className="history-table">
        <div className="history-row header"><span>Date</span><span>Distance</span><span>Load</span><span>Initial risk</span><span>Scenarios</span></div>
        {history.length === 0 && <div className="history-empty">No saved simulations yet.</div>}
        {history.map(item => (
          <div className="history-row" key={item.id}>
            <span>{new Date(item.created_at + "Z").toLocaleString()}</span>
            <span>{item.input.distance_km} km</span>
            <span>{item.input.vehicle_load_pct}%</span>
            <span className="probability">{Math.round(item.probability * 100)}%</span>
            <span>{item.scenarios.length}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

function RiskGraph({ profile }) {
  if (!profile) return <div className="lab-empty"><BarChart3 /><b>No graph yet</b><span>Adjust the mini simulator and generate a risk curve.</span></div>
  const width = 720, height = 300, pad = 44
  const points = profile.points.map((point, index) => ({
    ...point,
    x: pad + index * ((width - pad * 2) / (profile.points.length - 1)),
    y: pad + (1 - point.risk) * (height - pad * 2),
  }))
  const polyline = points.map(point => `${point.x},${point.y}`).join(" ")
  const factorName = profile.factor.replaceAll("_", " ")
  return (
    <div className="chart-wrap">
      <div className="chart-summary"><div><span>Current predicted risk</span><strong>{Math.round(profile.current_risk * 100)}%</strong></div><p>Risk response to changes in <b>{factorName}</b>.</p></div>
      <svg className="risk-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Delay-risk graph by ${factorName}`}>
        {[0, .25, .5, .75, 1].map(level => {
          const y = pad + (1 - level) * (height - pad * 2)
          return <g key={level}><line x1={pad} x2={width-pad} y1={y} y2={y} className="grid-line" /><text x={8} y={y+4}>{Math.round(level*100)}%</text></g>
        })}
        <polyline points={polyline} className="risk-line" />
        {points.map(point => <g key={point.value}><circle cx={point.x} cy={point.y} r="6" /><text x={point.x} y={height-12} textAnchor="middle">{point.value}</text><title>{point.value}: {Math.round(point.risk*100)}% risk</title></g>)}
      </svg>
    </div>
  )
}

function PredictLab({ token }) {
  const [shipment, setShipment] = useState(defaultShipment)
  const [factor, setFactor] = useState("vehicle_load_pct")
  const [profile, setProfile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const update = (name, value) => setShipment(previous => ({ ...previous, [name]: Number(value) }))
  async function generate() {
    setBusy(true)
    setError("")
    try {
      setProfile(await request("/api/risk-profile", { method: "POST", body: JSON.stringify({ ...shipment, factor }) }, token))
    } catch (err) {
      setError(err.message)
    } finally { setBusy(false) }
  }
  return (
    <div className="lab-grid">
      <section className="panel lab-controls">
        <div className="panel-heading"><div><span>PREDICT</span><h2>Risk sensitivity simulator</h2></div><Gauge /></div>
        <Field label="Vehicle load" value={shipment.vehicle_load_pct} suffix="%"><input type="range" min="25" max="100" value={shipment.vehicle_load_pct} onChange={e => update("vehicle_load_pct", e.target.value)} /></Field>
        <Field label="Departure" value={shipment.departure_hour} suffix=":00"><input type="range" min="0" max="23" value={shipment.departure_hour} onChange={e => update("departure_hour", e.target.value)} /></Field>
        <Field label="Schedule buffer" value={shipment.buffer_minutes} suffix=" min"><input type="range" min="0" max="120" step="5" value={shipment.buffer_minutes} onChange={e => update("buffer_minutes", e.target.value)} /></Field>
        <label className="field"><span>Graph factor</span><select value={factor} onChange={e => setFactor(e.target.value)}><option value="vehicle_load_pct">Vehicle load</option><option value="buffer_minutes">Schedule buffer</option><option value="departure_hour">Departure hour</option></select></label>
        {error && <div className="error">{error}</div>}
        <button className="primary" onClick={generate} disabled={busy}><BarChart3 size={18} />{busy ? "Generating…" : "Generate risk graph"}</button>
      </section>
      <section className="panel chart-panel"><RiskGraph profile={profile} /></section>
    </div>
  )
}

function VerifyLab({ token }) {
  const [check, setCheck] = useState({
    product_sealed: true, product_labeled: true, temperature_controlled: true,
    hazardous_documentation: true, load_secured: true, tire_condition: 90,
    brake_condition: 90, fuel_level: 75, maintenance_overdue: false, driver_rest_hours: 8,
  })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const toggle = name => setCheck(previous => ({ ...previous, [name]: !previous[name] }))
  const update = (name, value) => setCheck(previous => ({ ...previous, [name]: Number(value) }))
  async function verify() {
    setBusy(true)
    setError("")
    try {
      setResult(await request("/api/verify-safety", { method: "POST", body: JSON.stringify(check) }, token))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }
  const box = (name, label) => <label className="check-option"><input type="checkbox" checked={check[name]} onChange={() => toggle(name)} /><span>{label}</span></label>
  return (
    <div className="verify-grid">
      <section className="panel">
        <div className="panel-heading"><div><span>PRODUCT SAFETY</span><h2>Shipment verification</h2></div><PackageCheck /></div>
        <div className="check-grid">{box("product_sealed", "Packaging sealed")}{box("product_labeled", "Safety label attached")}{box("temperature_controlled", "Temperature requirement met")}{box("hazardous_documentation", "Hazard documents complete")}</div>
        <div className="section-divider" />
        <div className="panel-heading compact"><div><span>VEHICLE SAFETY</span><h2>Road-readiness verification</h2></div><ShieldCheck /></div>
        <div className="check-grid">{box("load_secured", "Cargo secured")}{box("maintenance_overdue", "Maintenance overdue")}</div>
        <Field label="Tire condition" value={check.tire_condition} suffix="%"><input type="range" min="0" max="100" value={check.tire_condition} onChange={e => update("tire_condition", e.target.value)} /></Field>
        <Field label="Brake condition" value={check.brake_condition} suffix="%"><input type="range" min="0" max="100" value={check.brake_condition} onChange={e => update("brake_condition", e.target.value)} /></Field>
        <Field label="Fuel level" value={check.fuel_level} suffix="%"><input type="range" min="0" max="100" value={check.fuel_level} onChange={e => update("fuel_level", e.target.value)} /></Field>
        <Field label="Driver rest" value={check.driver_rest_hours} suffix=" h"><input type="range" min="0" max="12" step=".5" value={check.driver_rest_hours} onChange={e => update("driver_rest_hours", e.target.value)} /></Field>
        {error && <div className="error">{error}</div>}
        <button className="primary" onClick={verify} disabled={busy}><ShieldCheck size={18} /> {busy ? "Verifying…" : "Verify dispatch safety"}</button>
      </section>
      <section className="panel verification-result">
        {!result ? <div className="lab-empty"><ShieldCheck /><b>Verification pending</b><span>Complete the checks to verify product and vehicle safety.</span></div> : <>
          <div className={`dispatch-status ${result.safe_to_dispatch ? "safe" : "blocked"}`}>{result.safe_to_dispatch ? <CheckCircle2 /> : <XCircle />}<div><span>Dispatch decision</span><h2>{result.safe_to_dispatch ? "Safe to dispatch" : "Dispatch blocked"}</h2></div></div>
          <div className="score-grid"><div><span>Product safety</span><strong>{result.product_score}%</strong></div><div><span>Vehicle safety</span><strong>{result.vehicle_score}%</strong></div><div><span>Overall</span><strong>{result.overall_score}%</strong></div></div>
          <div className="verification-lists"><CheckList title="Product checks" items={result.product_checks} /><CheckList title="Vehicle checks" items={result.vehicle_checks} /></div>
          <p className="notice">{result.notice}</p>
        </>}
      </section>
    </div>
  )
}

function CheckList({ title, items }) {
  return <div className="check-result-list"><h3>{title}</h3>{items.map(item => <div key={item.label} className={item.passed ? "pass" : "fail"}>{item.passed ? <CheckCircle2 /> : <XCircle />}<span>{item.label}</span></div>)}</div>
}

function RankLab({ token }) {
  const [shipment, setShipment] = useState(defaultShipment)
  const [drivers, setDrivers] = useState([])
  const [notice, setNotice] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const update = (name, value) => setShipment(previous => ({ ...previous, [name]: Number(value) }))
  async function rank() {
    setBusy(true)
    setError("")
    try {
      const data = await request("/api/rank-drivers", { method: "POST", body: JSON.stringify(shipment) }, token)
      setDrivers(data.drivers); setNotice(data.notice)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="rank-layout">
      <section className="panel rank-controls">
        <div className="panel-heading"><div><span>DRIVER RANKING</span><h2>Shipment risk context</h2></div><Users /></div>
        <Field label="Vehicle load" value={shipment.vehicle_load_pct} suffix="%"><input type="range" min="25" max="100" value={shipment.vehicle_load_pct} onChange={e => update("vehicle_load_pct", e.target.value)} /></Field>
        <label className="field"><span>Traffic</span><select value={shipment.traffic_level} onChange={e => update("traffic_level", e.target.value)}><option value="0">Clear</option><option value="1">Light</option><option value="2">Heavy</option><option value="3">Severe</option></select></label>
        <label className="field"><span>Weather</span><select value={shipment.weather_severity} onChange={e => update("weather_severity", e.target.value)}><option value="0">Clear</option><option value="1">Moderate</option><option value="2">Poor</option><option value="3">Severe</option></select></label>
        {error && <div className="error">{error}</div>}
        <button className="primary" onClick={rank} disabled={busy}><Award size={18} /> {busy ? "Ranking…" : "Rank drivers by risk"}</button>
      </section>
      <section className="driver-list">
        {drivers.length === 0 ? <div className="panel lab-empty tall"><Users /><b>No ranking yet</b><span>Set shipment conditions and rank the available drivers.</span></div> : drivers.map(driver => <article className="panel driver-card" key={driver.name}>
          <div className="rank-badge">#{driver.rank}</div>
          <div className="driver-identity"><div className="driver-avatar">{driver.name.split(" ").map(part => part[0]).join("")}</div><div><h3>{driver.name}</h3><span>{driver.experience} years · {driver.incidents} incident{driver.incidents === 1 ? "" : "s"} · {driver.rest_hours}h rest</span></div></div>
          <div className="driver-risk"><span>Predicted risk</span><strong>{Math.round(driver.risk*100)}%</strong><small>{Math.round(driver.safe_arrival_likelihood*100)}% lower-risk arrival likelihood</small></div>
          <div className="skill-tags">{driver.skills.map(skill => <span key={skill}>{skill}</span>)}</div>
          <div className="skill-recommendation"><Sparkles size={16} /><span><b>Risk-reduction skill:</b> {driver.recommended_skill}</span></div>
        </article>)}
        {notice && <p className="notice">{notice}</p>}
      </section>
    </div>
  )
}

function Method({ token }) {
  const [tool, setTool] = useState("predict")
  return <>
    <div className="tool-tabs">
      <button className={tool === "predict" ? "active" : ""} onClick={() => setTool("predict")}><BarChart3 /> Predict & graph</button>
      <button className={tool === "verify" ? "active" : ""} onClick={() => setTool("verify")}><ShieldCheck /> Verify safety</button>
      <button className={tool === "rank" ? "active" : ""} onClick={() => setTool("rank")}><Users /> Rank drivers</button>
    </div>
    {tool === "predict" && <PredictLab token={token} />}
    {tool === "verify" && <VerifyLab token={token} />}
    {tool === "rank" && <RankLab token={token} />}
  </>
}

function Dashboard({ session, onLogout }) {
  const [view, setView] = useState("simulate")
  const [refreshKey, setRefreshKey] = useState(0)
  const navigation = [
    ["simulate", Route, "Simulator"],
    ["history", History, "History"],
    ["method", BarChart3, "Decision Lab"],
  ]
  return (
    <div className="dashboard">
      <aside>
        <div className="side-brand"><Truck /> <b>RiskRoute</b></div>
        <nav>{navigation.map(([key, Icon, label]) => <button className={view === key ? "active" : ""} onClick={() => setView(key)} key={key}><Icon size={19} />{label}</button>)}</nav>
        <div className="side-user"><div className="avatar">{session.user.name[0].toUpperCase()}</div><div><b>{session.user.name}</b><small>{session.user.email}</small></div><button onClick={onLogout} title="Sign out"><LogOut size={18} /></button></div>
      </aside>
      <main className="content">
        <header><div><span>INTELLIGENT LOGISTICS</span><h1>{view === "simulate" ? "What-if decision simulator" : view === "history" ? "Saved decisions" : "Decision intelligence lab"}</h1></div><div className="status"><i></i> Model online</div></header>
        {view === "simulate" && <Simulator token={session.token} onSaved={() => setRefreshKey(k => k + 1)} />}
        {view === "history" && <HistoryView token={session.token} refreshKey={refreshKey} />}
        {view === "method" && <Method token={session.token} />}
      </main>
    </div>
  )
}

export default function App() {
  const [session, setSession] = useState(() => {
    try { return JSON.parse(localStorage.getItem("cfx-session")) } catch { return null }
  })
  function saveSession(value) {
    localStorage.setItem("cfx-session", JSON.stringify(value))
    setSession(value)
  }
  function logout() {
    localStorage.removeItem("cfx-session")
    setSession(null)
  }
  return session ? <Dashboard session={session} onLogout={logout} /> : <Auth onSuccess={saveSession} />
}
