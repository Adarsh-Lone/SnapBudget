import React, { useEffect, useState } from "react";
import Dashboard from "./components/Dashboard";

const API_BASE = "http://localhost:5000";

function App() {
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);

  const loadData = async () => {
    try {
      const [summaryRes, txRes] = await Promise.all([
        fetch(`${API_BASE}/api/analytics/summary?user_id=1`),
        fetch(`${API_BASE}/api/transactions?user_id=1`),
      ]);
      const summaryJson = await summaryRes.json();
      const txJson = await txRes.json();
      setSummary(summaryJson);
      setTransactions(txJson.transactions || []);
    } catch (e) {
      console.error("Failed to load data", e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSmsSubmit = async (text) => {
    try {
      await fetch(`${API_BASE}/api/transactions/parse-sms`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, user_id: 1 }),
      });
      await loadData();
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
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Dashboard
      summary={summary}
      transactions={transactions}
      onSmsSubmit={handleSmsSubmit}
      onReceiptUpload={handleReceiptUpload}
    />
  );
}

export default App;

