import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard";

const API_BASE = "http://localhost:5000";

function AppShell({ children }) {
  return (
    <div
      style={{
        height: "100vh",
        overflow: "hidden",
        background:
          "radial-gradient(circle at top left, #0ea5e9 0, transparent 45%), radial-gradient(circle at bottom right, #22c55e 0, #020617 55%)",
        color: "#f9fafb",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <nav
        style={{
          padding: "12px 24px",
          borderBottom: "1px solid rgba(148,163,184,0.35)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ fontSize: 18, fontWeight: 600 }}>SnapBudget OCR+</div>
        <div style={{ display: "flex", gap: 16, fontSize: 13 }}>
          <NavLink
            to="/"
            end
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: "6px 10px",
              borderRadius: 999,
              color: isActive ? "#0f172a" : "#e5e7eb",
              background: isActive
                ? "linear-gradient(135deg,#22c55e,#0ea5e9)"
                : "transparent",
            })}
          >
            Overview
          </NavLink>
          <NavLink
            to="/profile"
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: "6px 10px",
              borderRadius: 999,
              color: isActive ? "#0f172a" : "#e5e7eb",
              background: isActive
                ? "linear-gradient(135deg,#22c55e,#0ea5e9)"
                : "transparent",
            })}
          >
            Profile
          </NavLink>
          <NavLink
            to="/analytics"
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: "6px 10px",
              borderRadius: 999,
              color: isActive ? "#0f172a" : "#e5e7eb",
              background: isActive
                ? "linear-gradient(135deg,#22c55e,#0ea5e9)"
                : "transparent",
            })}
          >
            Analytics
          </NavLink>
          <NavLink
            to="/alerts"
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: "6px 10px",
              borderRadius: 999,
              color: isActive ? "#0f172a" : "#e5e7eb",
              background: isActive
                ? "linear-gradient(135deg,#22c55e,#0ea5e9)"
                : "transparent",
            })}
          >
            Alerts
          </NavLink>
          <NavLink
            to="/insights"
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: "6px 10px",
              borderRadius: 999,
              color: isActive ? "#0f172a" : "#e5e7eb",
              background: isActive
                ? "linear-gradient(135deg,#22c55e,#0ea5e9)"
                : "transparent",
            })}
          >
            Insights
          </NavLink>
        </div>
      </nav>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          overflowX: "hidden",
          padding: "16px",
          display: "flex",
          justifyContent: "center",
          alignItems: "stretch",
        }}
      >
        <div style={{ width: "100%", maxWidth: 1120 }}>{children}</div>
      </div>
    </div>
  );
}

function App() {
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [profile, setProfile] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [alertsContext, setAlertsContext] = useState(null);
  const [graphs, setGraphs] = useState(null);
  const [behavior, setBehavior] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [insights, setInsights] = useState([]);

  const loadCore = async () => {
    const [summaryRes, txRes] = await Promise.all([
      fetch(`${API_BASE}/api/analytics/summary?user_id=1`),
      fetch(`${API_BASE}/api/transactions?user_id=1`),
    ]);
    const summaryJson = await summaryRes.json();
    const txJson = await txRes.json();
    setSummary(summaryJson);
    setTransactions(txJson.transactions || []);
  };

  const loadAdvanced = async () => {
    try {
      const [
        profileRes,
        alertsRes,
        graphsRes,
        behaviorRes,
        predictionsRes,
        insightsRes,
      ] = await Promise.all([
        fetch(`${API_BASE}/api/profile?user_id=1`),
        fetch(`${API_BASE}/api/alerts?user_id=1`),
        fetch(`${API_BASE}/api/analytics/graphs?user_id=1`),
        fetch(`${API_BASE}/api/behavior?user_id=1`),
        fetch(`${API_BASE}/api/predictions?user_id=1`),
        fetch(`${API_BASE}/api/insights?user_id=1`),
      ]);

      const profileJson = await profileRes.json();
      const alertsJson = await alertsRes.json();
      const graphsJson = await graphsRes.json();
      const behaviorJson = await behaviorRes.json();
      const predictionsJson = await predictionsRes.json();
      const insightsJson = await insightsRes.json();

      setProfile(profileJson);
      setAlerts(alertsJson.alerts || []);
      setAlertsContext(alertsJson.context || null);
      setGraphs(graphsJson);
      setBehavior(behaviorJson);
      setPredictions(predictionsJson);
      setInsights(insightsJson.insights || []);
    } catch (e) {
      console.error("Failed to load advanced analytics", e);
    }
  };

  const refreshAll = async () => {
    await loadCore();
    await loadAdvanced();
  };

  useEffect(() => {
    refreshAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSmsSubmit = async (text) => {
    try {
      await fetch(`${API_BASE}/api/transactions/parse-sms`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, user_id: 1 }),
      });
      await refreshAll();
    } catch (e) {
      console.error(e);
    }
  };

  const handleReceiptUpload = async (file) => {
    const form = new FormData();
    form.append("file", file);
    form.append("user_id", "1");
    try {
      await fetch(`${API_BASE}/api/transactions/upload-receipt`, {
        method: "POST",
        body: form,
      });
      await refreshAll();
    } catch (e) {
      console.error(e);
    }
  };

  const handleProfileSave = async (payload) => {
    try {
      const res = await fetch(`${API_BASE}/api/profile?user_id=1`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const json = await res.json();
      setProfile(json);
      await loadAdvanced();
    } catch (e) {
      console.error("Failed to save profile", e);
    }
  };

  return (
    <Router>
      <AppShell>
        <Routes>
          <Route
            path="/"
            element={
              <Dashboard
                summary={summary}
                transactions={transactions}
                profile={profile}
                alerts={alerts}
                alertsContext={alertsContext}
                graphs={graphs}
                behavior={behavior}
                predictions={predictions}
                insights={insights}
                onSmsSubmit={handleSmsSubmit}
                onReceiptUpload={handleReceiptUpload}
                onProfileSave={handleProfileSave}
                forcedSection="overview"
                showSidebar={false}
              />
            }
          />
          <Route
            path="/profile"
            element={
              <Dashboard
                summary={summary}
                transactions={transactions}
                profile={profile}
                alerts={alerts}
                alertsContext={alertsContext}
                graphs={graphs}
                behavior={behavior}
                predictions={predictions}
                insights={insights}
                onSmsSubmit={handleSmsSubmit}
                onReceiptUpload={handleReceiptUpload}
                onProfileSave={handleProfileSave}
                forcedSection="profile"
                showSidebar={false}
              />
            }
          />
          <Route
            path="/analytics"
            element={
              <Dashboard
                summary={summary}
                transactions={transactions}
                profile={profile}
                alerts={alerts}
                alertsContext={alertsContext}
                graphs={graphs}
                behavior={behavior}
                predictions={predictions}
                insights={insights}
                onSmsSubmit={handleSmsSubmit}
                onReceiptUpload={handleReceiptUpload}
                onProfileSave={handleProfileSave}
                forcedSection="analytics"
                showSidebar={false}
              />
            }
          />
          <Route
            path="/alerts"
            element={
              <Dashboard
                summary={summary}
                transactions={transactions}
                profile={profile}
                alerts={alerts}
                alertsContext={alertsContext}
                graphs={graphs}
                behavior={behavior}
                predictions={predictions}
                insights={insights}
                onSmsSubmit={handleSmsSubmit}
                onReceiptUpload={handleReceiptUpload}
                onProfileSave={handleProfileSave}
                forcedSection="alerts"
                showSidebar={false}
              />
            }
          />
          <Route
            path="/insights"
            element={
              <Dashboard
                summary={summary}
                transactions={transactions}
                profile={profile}
                alerts={alerts}
                alertsContext={alertsContext}
                graphs={graphs}
                behavior={behavior}
                predictions={predictions}
                insights={insights}
                onSmsSubmit={handleSmsSubmit}
                onReceiptUpload={handleReceiptUpload}
                onProfileSave={handleProfileSave}
                forcedSection="alerts"
                showSidebar={false}
              />
            }
          />
        </Routes>
      </AppShell>
    </Router>
  );
}

export default App;

