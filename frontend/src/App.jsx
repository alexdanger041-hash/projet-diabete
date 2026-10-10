import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from "recharts";
import { api } from "./api";

const AVERT = "Outil pédagogique de sensibilisation : estimation statistique, pas un diagnostic médical. Consultez un professionnel de santé.";

const CHAMPS = [
  ["pregnancies", "Nombre de grossesses", "0 à 20"],
  ["glucose", "Glucose (mg/dL)", "40 à 300"],
  ["blood_pressure", "Tension diastolique (mm Hg)", "30 à 200"],
  ["skin_thickness", "Épaisseur du pli cutané (mm)", "5 à 100"],
  ["insulin", "Insuline (µU/mL)", "10 à 900"],
  ["bmi", "IMC", "10 à 70"],
  ["pedigree", "Antécédents familiaux (indice)", "0,05 à 2,5"],
  ["age", "Âge", "18 à 100"],
];

const COULEUR = { faible: "#2e9e5b", modéré: "#e08a00", élevé: "#d33a3a" };

function anonId() {
  let id = localStorage.getItem("anon_id");
  if (!id) {
    id = crypto.randomUUID ? crypto.randomUUID() : "anon-" + Math.random().toString(36).slice(2) + Date.now();
    localStorage.setItem("anon_id", id);
  }
  return id;
}

function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    try {
      if (mode === "register") await api("/auth/register", { method: "POST", body: { email, password } });
      const d = await api("/auth/login", { method: "POST", form: { username: email, password } });
      onLogin(d.access_token, d.role);
    } catch (x) {
      setErr(x.message);
    }
  }

  return (
    <form className="carte" onSubmit={submit}>
      <h2>{mode === "login" ? "Connexion" : "Créer un compte"}</h2>
      <p>Découvrez, à titre pédagogique, les facteurs qui influencent le risque de diabète.</p>
      <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
      <label>Mot de passe (8 caractères minimum)<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} /></label>
      {err && <p className="erreur">{err}</p>}
      <button type="submit">{mode === "login" ? "Se connecter" : "S'inscrire"}</button>
      <button type="button" className="lien" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Pas de compte ? S'inscrire" : "Déjà un compte ? Se connecter"}
      </button>
    </form>
  );
}

function Questionnaire({ token }) {
  const [vals, setVals] = useState({});
  const [res, setRes] = useState(null);
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    const body = { anon_id: anonId() };
    CHAMPS.forEach(([k]) => (body[k] = Number(vals[k])));
    try {
      setRes(await api("/predict", { method: "POST", body, token }));
    } catch (x) {
      setErr(x.message);
    }
  }

  return (
    <>
      <form className="carte" onSubmit={submit}>
        <h2>Questionnaire</h2>
        <div className="grille">
          {CHAMPS.map(([k, label, plage]) => (
            <label key={k}>{label} <small>({plage})</small>
              <input type="number" step="any" required value={vals[k] ?? ""}
                onChange={(e) => setVals({ ...vals, [k]: e.target.value })} />
            </label>
          ))}
        </div>
        {err && <p className="erreur">{err}</p>}
        <button type="submit">Estimer le risque</button>
      </form>

      {res && (
        <div className="carte">
          <h2>Résultat</h2>
          <p className="score" style={{ color: COULEUR[res.niveau] }}>
            {Math.round(res.probabilite * 100)} % — risque {res.niveau}
          </p>
          <h3>Facteurs qui influencent l'estimation</h3>
          <small>Rouge : augmente le risque — Vert : le diminue</small>
          <div style={{ width: "100%", height: 320 }}>
            <ResponsiveContainer>
              <BarChart data={res.facteurs} layout="vertical" margin={{ left: 30 }}>
                <XAxis type="number" />
                <YAxis type="category" dataKey="variable" width={150} />
                <Tooltip />
                <Bar dataKey="impact">
                  {res.facteurs.map((f, i) => <Cell key={i} fill={f.impact > 0 ? "#d33a3a" : "#2e9e5b"} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <h3>Recommandations générales</h3>
          <ul>{res.recommandations.map((r, i) => <li key={i}>{r}</li>)}</ul>
          <p className="avert">{res.avertissement}</p>
        </div>
      )}
    </>
  );
}

function Historique({ token }) {
  const [rows, setRows] = useState(null);
  useEffect(() => {
    api(`/history?anon_id=${anonId()}`, { token }).then(setRows).catch(() => setRows([]));
  }, [token]);
  if (!rows) return <p>Chargement…</p>;
  return (
    <div className="carte">
      <h2>Historique anonyme (ce navigateur)</h2>
      {rows.length === 0 ? <p>Aucune estimation pour le moment.</p> : (
        <div className="defil">
          <table>
            <thead><tr><th>Date</th><th>Risque</th><th>Niveau</th><th>Glucose</th><th>IMC</th><th>Âge</th></tr></thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  <td>{new Date(r.date).toLocaleString("fr-FR")}</td>
                  <td>{Math.round(r.probabilite * 100)} %</td>
                  <td>{r.niveau}</td><td>{r.glucose}</td><td>{r.bmi}</td><td>{r.age}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Dashboard({ token }) {
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    api("/admin/dashboard", { token }).then(setD).catch((x) => setErr(x.message));
  }, [token]);
  if (err) return <p className="erreur">{err}</p>;
  if (!d) return <p>Chargement…</p>;
  const niveaux = ["faible", "modéré", "élevé"].map((n) => ({ niveau: n, total: d.par_niveau[n] || 0 }));
  return (
    <div className="carte">
      <h2>Dashboard agrégé</h2>
      <p className="score">{d.total_predictions} estimations réalisées</p>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <BarChart data={niveaux}>
            <XAxis dataKey="niveau" /><YAxis allowDecimals={false} /><Tooltip />
            <Bar dataKey="total">{niveaux.map((n, i) => <Cell key={i} fill={COULEUR[n.niveau]} />)}</Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ul>
        <li>Glucose moyen : {d.moyennes.glucose}</li>
        <li>IMC moyen : {d.moyennes.bmi}</li>
        <li>Âge moyen : {d.moyennes.age}</li>
        <li>Risque moyen : {Math.round(d.moyennes.probabilite * 100)} %</li>
      </ul>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [role, setRole] = useState(localStorage.getItem("role"));
  const [page, setPage] = useState("questionnaire");

  function onLogin(t, r) {
    localStorage.setItem("token", t);
    localStorage.setItem("role", r);
    setToken(t); setRole(r);
    setPage(r === "admin" ? "dashboard" : "questionnaire");
  }
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setToken(null); setRole(null);
  }

  return (
    <>
      <div className="banniere">{AVERT}</div>
      <header>
        <h1>Risque de diabète — sensibilisation</h1>
        {token && (
          <nav>
            {role === "user" && <button onClick={() => setPage("questionnaire")}>Questionnaire</button>}
            {role === "user" && <button onClick={() => setPage("historique")}>Historique</button>}
            {role === "admin" && <button onClick={() => setPage("dashboard")}>Dashboard</button>}
            <button className="lien" onClick={logout}>Déconnexion</button>
          </nav>
        )}
      </header>
      <main>
        {!token && <Auth onLogin={onLogin} />}
        {token && page === "questionnaire" && role === "user" && <Questionnaire token={token} />}
        {token && page === "historique" && role === "user" && <Historique token={token} />}
        {token && page === "dashboard" && role === "admin" && <Dashboard token={token} />}
      </main>
    </>
  );
}