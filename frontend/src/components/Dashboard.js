import React, { useState } from "react";
import TransactionsTable from "./TransactionsTable";

function StatCard({ label, value, accent }) {
  return (
    <div
      style={{
        padding: "16px",
        borderRadius: "12px",
        background:
          "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.9))",
        border: `1px solid ${accent || "rgba(148,163,184,0.4)"}`,
        boxShadow: "0 18px 45px rgba(15, 23, 42, 0.85)",
      }}
    >
      <div style={{ fontSize: 13, color: "#9ca3af", marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: 22, fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function Dashboard({ summary, transactions, onSmsSubmit, onReceiptUpload }) {
  const [smsText, setSmsText] = useState("");

  const handleSmsForm = (e) => {
    e.preventDefault();
    if (!smsText.trim()) return;
    onSmsSubmit(smsText.trim());
    setSmsText("");
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onReceiptUpload(e.target.files[0]);
      e.target.value = "";
    }
  };

  const s = summary || {};

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, #0ea5e9 0, transparent 45%), radial-gradient(circle at bottom right, #22c55e 0, #020617 55%)",
        padding: "32px 16px 48px",
        color: "#f9fafb",
      }}
    >
      <div
        style={{
          maxWidth: 1120,
          margin: "0 auto",
        }}
      >
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 24,
            gap: 16,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 12,
                textTransform: "uppercase",
                letterSpacing: 2,
                color: "#a5b4fc",
                marginBottom: 4,
              }}
            >
              SnapBudget OCR+
            </div>
            <h1
              style={{
                margin: 0,
                fontSize: 26,
                fontWeight: 650,
              }}
            >
              Intelligent Passive Expense Tracker
            </h1>
            <p
              style={{
                margin: "6px 0 0",
                fontSize: 13,
                color: "#9ca3af",
              }}
            >
              Drop in your debit SMS or receipt image. Watch your burn rate and
              survival days update in real time.
            </p>
          </div>
          <div
            style={{
              padding: "8px 14px",
              borderRadius: 999,
              border: "1px solid rgba(148,163,184,0.35)",
              fontSize: 12,
              background:
                "linear-gradient(145deg, rgba(15,23,42,0.95), rgba(15,23,42,0.9))",
            }}
          >
            API: <code>http://localhost:5000</code>
          </div>
        </header>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1.4fr",
            gap: 20,
            alignItems: "flex-start",
          }}
        >
          <div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))",
                gap: 14,
                marginBottom: 16,
              }}
            >
              <StatCard
                label="Average Daily Spend"
                value={
                  s.avg_daily_spend != null
                    ? `₹${s.avg_daily_spend}`
                    : "—"
                }
              />
              <StatCard
                label="Spending Volatility"
                value={
                  s.spending_volatility != null
                    ? `₹${s.spending_volatility}`
                    : "—"
                }
              />
              <StatCard
                label="Burn Rate (last 30d)"
                value={s.burn_rate != null ? `₹${s.burn_rate}` : "—"}
              />
              <StatCard
                label="Survival Days"
                value={s.survival_days != null ? s.survival_days : "—"}
                accent="rgba(52,211,153,0.7)"
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit,minmax(190px,1fr))",
                gap: 14,
                marginBottom: 18,
              }}
            >
              <StatCard
                label="This Month vs Last"
                value={
                  s.current_month_spend != null
                    ? `₹${s.current_month_spend} vs ₹${s.previous_month_spend}`
                    : "—"
                }
              />
              <StatCard
                label="Financial Stress Date"
                value={s.stress_date || "—"}
                accent="rgba(248,113,113,0.9)"
              />
              <StatCard
                label="Behavior Tag"
                value={s.behavior_tag || "—"}
                accent="rgba(129,140,248,0.9)"
              />
            </div>

            <div
              style={{
                padding: 16,
                borderRadius: 12,
                background:
                  "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92))",
                border: "1px solid rgba(148,163,184,0.35)",
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 16 }}>
                Recent Transactions
              </h3>
              <TransactionsTable transactions={transactions} />
            </div>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
          >
            <div
              style={{
                padding: 16,
                borderRadius: 12,
                background:
                  "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92))",
                border: "1px solid rgba(148,163,184,0.35)",
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 15 }}>
                Paste Debit SMS
              </h3>
              <p style={{ marginTop: 0, fontSize: 12, color: "#9ca3af" }}>
                Works best with Indian-style debit alerts. We auto-extract
                amount, merchant, bank, and date.
              </p>
              <form onSubmit={handleSmsForm}>
                <textarea
                  rows="4"
                  placeholder="e.g. INR 799.00 spent on HDFC Bank CREDIT Card ending 1234 at NETFLIX.COM on 2026-03-02"
                  value={smsText}
                  onChange={(e) => setSmsText(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: 8,
                    border: "1px solid #1f2937",
                    background: "#020617",
                    color: "#f9fafb",
                    fontSize: 13,
                    resize: "vertical",
                    marginBottom: 10,
                  }}
                />
                <button type="submit">Parse SMS &amp; Save</button>
              </form>
            </div>

            <div
              style={{
                padding: 16,
                borderRadius: 12,
                background:
                  "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92))",
                border: "1px solid rgba(148,163,184,0.35)",
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 15 }}>
                Upload Receipt Image
              </h3>
              <p style={{ marginTop: 0, fontSize: 12, color: "#9ca3af" }}>
                JPG or PNG. Backend uses Tesseract OCR to pull amount, date and
                merchant.
              </p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{
                  marginTop: 4,
                  padding: 6,
                  background: "#020617",
                  borderRadius: 8,
                  border: "1px solid #1f2937",
                  color: "#f9fafb",
                }}
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;

