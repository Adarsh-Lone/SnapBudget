import React, { useState } from "react";
import TransactionsTable from "./TransactionsTable";
import AnalyticsCharts from "./AnalyticsCharts";

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

function Sidebar({ active, onChange }) {
  const items = [
    { key: "overview", label: "Overview" },
    { key: "profile", label: "Profile" },
    { key: "analytics", label: "Analytics" },
    { key: "alerts", label: "Alerts & Insights" },
  ];
  return (
    <div
      style={{
        width: 190,
        padding: 14,
        borderRadius: 16,
        background:
          "linear-gradient(160deg, rgba(15,23,42,0.98), rgba(15,23,42,0.9))",
        border: "1px solid rgba(148,163,184,0.45)",
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <div
        style={{
          fontSize: 13,
          letterSpacing: 1,
          textTransform: "uppercase",
          color: "#9ca3af",
          marginBottom: 6,
        }}
      >
        Sections
      </div>
      {items.map((it) => {
        const isActive = active === it.key;
        return (
          <button
            key={it.key}
            onClick={() => onChange(it.key)}
            style={{
              textAlign: "left",
              padding: "8px 10px",
              borderRadius: 999,
              border: "none",
              cursor: "pointer",
              fontSize: 13,
              color: isActive ? "#0f172a" : "#e5e7eb",
              background: isActive
                ? "linear-gradient(135deg,#22c55e,#0ea5e9)"
                : "rgba(15,23,42,0.9)",
              boxShadow: isActive
                ? "0 8px 22px rgba(34,197,94,0.4)"
                : "0 0 0 transparent",
            }}
          >
            {it.label}
          </button>
        );
      })}
    </div>
  );
}

function FinancialHealthChip({ summary, profile }) {
  if (!summary && !profile) return null;
  const income = profile?.income || 0;
  const fixedTotal = profile?.fixed_expenses_total || 0;
  const limit = profile?.monthly_limit || 0;
  const monthSpend = summary?.current_month_spend || 0;

  let score = 50;
  if (income > 0) {
    const fixedRatio = fixedTotal / income;
    if (fixedRatio < 0.4) score += 15;
    else if (fixedRatio > 0.7) score -= 15;
  }
  if (limit > 0) {
    const util = monthSpend / limit;
    if (util < 0.7) score += 15;
    else if (util > 1.1) score -= 20;
  }
  if (summary?.survival_days != null) {
    if (summary.survival_days >= 60) score += 10;
    else if (summary.survival_days < 30) score -= 15;
  }
  score = Math.max(0, Math.min(100, Math.round(score)));

  let label = "Okay";
  let color = "#facc15";
  let bg = "rgba(234,179,8,0.15)";
  if (score >= 75) {
    label = "Healthy";
    color = "#22c55e";
    bg = "rgba(34,197,94,0.18)";
  } else if (score <= 45) {
    label = "At Risk";
    color = "#f97316";
    bg = "rgba(248,113,22,0.22)";
  }

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "6px 12px",
        borderRadius: 999,
        background: bg,
        border: `1px solid ${color}33`,
        fontSize: 12,
      }}
    >
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          backgroundColor: color,
          boxShadow: `0 0 12px ${color}`,
        }}
      />
      <span style={{ color }}>{label}</span>
      <span style={{ color: "#9ca3af" }}>Score {score}/100</span>
    </div>
  );
}

function ProfileForm({ profile, onSave }) {
  const [local, setLocal] = useState(() => ({
    income: profile?.income || "",
    monthly_limit: profile?.monthly_limit || "",
    savings_goal: profile?.savings_goal || "",
    currency: profile?.currency || "INR",
    profile_picture_url: profile?.profile_picture_url || "",
    fixed_expenses_json: JSON.stringify(profile?.fixed_expenses || [], null, 2),
  }));

  const handleChange = (field, value) => {
    setLocal((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let fixed;
    try {
      fixed = JSON.parse(local.fixed_expenses_json || "[]");
    } catch (err) {
      alert("Fixed expenses must be valid JSON array");
      return;
    }
    onSave({
      income: Number(local.income || 0),
      monthly_limit: Number(local.monthly_limit || 0),
      savings_goal: Number(local.savings_goal || 0),
      currency: local.currency || "INR",
      profile_picture_url: local.profile_picture_url || null,
      fixed_expenses: fixed,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))",
          gap: 12,
        }}
      >
        <Field
          label="Monthly Income"
          type="number"
          value={local.income}
          onChange={(e) => handleChange("income", e.target.value)}
        />
        <Field
          label="Monthly Limit"
          type="number"
          value={local.monthly_limit}
          onChange={(e) => handleChange("monthly_limit", e.target.value)}
        />
        <Field
          label="Savings Goal"
          type="number"
          value={local.savings_goal}
          onChange={(e) => handleChange("savings_goal", e.target.value)}
        />
        <Field
          label="Currency"
          value={local.currency}
          onChange={(e) => handleChange("currency", e.target.value)}
        />
      </div>
      <Field
        label="Profile Picture URL"
        value={local.profile_picture_url}
        onChange={(e) => handleChange("profile_picture_url", e.target.value)}
      />
      <div>
        <label
          style={{
            display: "block",
            fontSize: 12,
            color: "#9ca3af",
            marginBottom: 4,
          }}
        >
          Fixed Expenses JSON
        </label>
        <textarea
          rows="4"
          value={local.fixed_expenses_json}
          onChange={(e) => handleChange("fixed_expenses_json", e.target.value)}
          style={{
            width: "100%",
            padding: "8px 10px",
            borderRadius: 8,
            border: "1px solid #1f2937",
            background: "#020617",
            color: "#f9fafb",
            fontSize: 12,
            resize: "vertical",
          }}
        />
        <div style={{ fontSize: 11, color: "#6b7280", marginTop: 4 }}>
          Example:{" "}
          <code>
            [{`{"name":"Rent","amount":25000},{"name":"EMI","amount":12000}`}]
          </code>
        </div>
      </div>
      <button
        type="submit"
        style={{
          alignSelf: "flex-start",
          marginTop: 4,
          padding: "8px 14px",
          borderRadius: 999,
          border: "none",
          cursor: "pointer",
          fontSize: 13,
          fontWeight: 500,
          color: "#0f172a",
          background:
            "linear-gradient(135deg, rgba(34,197,94,1), rgba(14,165,233,1))",
          boxShadow: "0 12px 30px rgba(34,197,94,0.45)",
        }}
      >
        Save Profile
      </button>
    </form>
  );
}

function Field({ label, ...inputProps }) {
  return (
    <div>
      <label
        style={{
          display: "block",
          fontSize: 12,
          color: "#9ca3af",
          marginBottom: 3,
        }}
      >
        {label}
      </label>
      <input
        {...inputProps}
        style={{
          width: "100%",
          padding: "8px 10px",
          borderRadius: 8,
          border: "1px solid #1f2937",
          background: "#020617",
          color: "#f9fafb",
          fontSize: 13,
        }}
      />
    </div>
  );
}

function AlertsPanel({ alerts, alertsContext, insights }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {alerts?.length ? (
        alerts.map((a, idx) => (
          <div
            key={idx}
            style={{
              padding: 10,
              borderRadius: 10,
              border: "1px solid rgba(148,163,184,0.4)",
              background:
                a.severity === "critical"
                  ? "linear-gradient(135deg, rgba(248,113,113,0.22), rgba(15,23,42,0.98))"
                  : "linear-gradient(135deg, rgba(250,204,21,0.18), rgba(15,23,42,0.98))",
            }}
          >
            <div
              style={{
                fontSize: 12,
                textTransform: "uppercase",
                letterSpacing: 1,
                color: "#9ca3af",
                marginBottom: 3,
              }}
            >
              {a.type}
            </div>
            <div style={{ fontSize: 14 }}>{a.message}</div>
          </div>
        ))
      ) : (
        <div style={{ fontSize: 13, color: "#9ca3af" }}>
          No active distress alerts. Keep tracking your spending.
        </div>
      )}
      {alertsContext && (
        <div
          style={{
            marginTop: 6,
            padding: 10,
            borderRadius: 10,
            border: "1px dashed rgba(148,163,184,0.4)",
            fontSize: 12,
            color: "#9ca3af",
          }}
        >
          <div>
            Burn rate: <strong>₹{alertsContext.burn_rate}</strong> / month, runway:{" "}
            <strong>
              {alertsContext.runway_days != null
                ? `${alertsContext.runway_days.toFixed(1)} days`
                : "—"}
            </strong>
          </div>
          <div style={{ marginTop: 2 }}>
            Weekly burn:{" "}
            <strong>₹{alertsContext.weekly_burn_rate_current} this week</strong> vs{" "}
            <strong>₹{alertsContext.weekly_burn_rate_previous} last week</strong>
          </div>
        </div>
      )}
      {!!insights?.length && (
        <div
          style={{
            marginTop: 8,
            paddingTop: 8,
            borderTop: "1px dashed rgba(31,41,55,1)",
          }}
        >
          <div
            style={{
              fontSize: 13,
              color: "#e5e7eb",
              marginBottom: 4,
              fontWeight: 500,
            }}
          >
            Transaction Insights
          </div>
          <ul
            style={{
              listStyle: "none",
              paddingLeft: 0,
              margin: 0,
              fontSize: 12,
              color: "#9ca3af",
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
          >
            {insights.map((i, idx) => (
              <li key={idx}>• {i.message}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Dashboard({
  summary,
  transactions,
  profile,
  alerts,
  alertsContext,
  graphs,
  behavior,
  predictions,
  insights,
  onSmsSubmit,
  onReceiptUpload,
  onProfileSave,
  forcedSection,
  showSidebar = true,
}) {
  const [smsText, setSmsText] = useState("");
  const [activeSection, setActiveSection] = useState(forcedSection || "overview");

  if (forcedSection && activeSection !== forcedSection) {
    // keep UI in sync with route-driven section
    setActiveSection(forcedSection);
  }

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
        height: "auto",
        overflow: "visible",
        padding: "16px 0 24px",
        color: "#f9fafb",
        display: "flex",
        flexDirection: "column",
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
            gridTemplateColumns: showSidebar
              ? "220px minmax(0,1.6fr) minmax(0,1.2fr)"
              : "minmax(0,1.7fr) minmax(0,1.3fr)",
            gap: 20,
            alignItems: "stretch",
            minHeight: 0,
          }}
        >
          {showSidebar && (
            <Sidebar active={activeSection} onChange={setActiveSection} />
          )}
          <div style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
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

            {activeSection === "overview" && (
              <div
                style={{
                  padding: 16,
                  borderRadius: 12,
                  background:
                    "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92))",
                  border: "1px solid rgba(148,163,184,0.35)",
                  display: "flex",
                  flexDirection: "column",
                  height: "100%",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 8,
                    gap: 12,
                  }}
                >
                  <h3 style={{ margin: 0, fontSize: 16 }}>Recent Transactions</h3>
                  <FinancialHealthChip summary={summary} profile={profile} />
                </div>
                <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
                  <TransactionsTable transactions={transactions} />
                </div>
              </div>
            )}
            {activeSection === "profile" && (
              <div
                style={{
                  padding: 16,
                  borderRadius: 12,
                  background:
                    "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92))",
                  border: "1px solid rgba(148,163,184,0.35)",
                  display: "grid",
                  gridTemplateColumns: "minmax(0,1.4fr) minmax(0,1fr)",
                  gap: 16,
                }}
              >
                <div>
                  <h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 16 }}>
                    Profile & Budget Settings
                  </h3>
                  <ProfileForm profile={profile} onSave={onProfileSave} />
                </div>
                <div style={{ alignSelf: "flex-start" }}>
                  <h4
                    style={{
                      marginTop: 0,
                      marginBottom: 8,
                      fontSize: 14,
                      color: "#e5e7eb",
                    }}
                  >
                    Snapshot
                  </h4>
                  <FinancialHealthChip summary={summary} profile={profile} />
                  <div style={{ fontSize: 12, color: "#9ca3af", marginTop: 10 }}>
                    Use this panel to tune income, fixed expenses, and monthly limits.
                    Your alerts and analytics will automatically adapt to your
                    configuration.
                  </div>
                </div>
              </div>
            )}
            {activeSection === "analytics" && (
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
                  Analytics Dashboard
                </h3>
                <AnalyticsCharts graphs={graphs} />
              </div>
            )}
            {activeSection === "alerts" && (
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
                  Alerts & Insights
                </h3>
                <AlertsPanel
                  alerts={alerts}
                  alertsContext={alertsContext}
                  insights={insights}
                />
                {behavior && (
                  <div
                    style={{
                      marginTop: 14,
                      paddingTop: 10,
                      borderTop: "1px dashed rgba(31,41,55,1)",
                      fontSize: 13,
                    }}
                  >
                    <div style={{ color: "#e5e7eb", marginBottom: 4 }}>
                      Behavior Tag:{" "}
                      <span
                        style={{
                          padding: "3px 9px",
                          borderRadius: 999,
                          border: "1px solid rgba(129,140,248,0.6)",
                          background: "rgba(17,24,39,0.9)",
                          fontSize: 12,
                        }}
                      >
                        {behavior.tag}
                      </span>
                    </div>
                  </div>
                )}
                {predictions && (
                  <div
                    style={{
                      marginTop: 8,
                      padding: 10,
                      borderRadius: 10,
                      background:
                        "linear-gradient(135deg, rgba(56,189,248,0.18), rgba(15,23,42,0.98))",
                      border: "1px solid rgba(56,189,248,0.4)",
                      fontSize: 12,
                      color: "#e5e7eb",
                    }}
                  >
                    <div style={{ marginBottom: 2 }}>
                      Projected stress date:{" "}
                      <strong>
                        {predictions.financial_stress_date || "No stress projected"}
                      </strong>
                    </div>
                    <div>
                      Confidence:{" "}
                      <strong>{Math.round((predictions.confidence_score || 0) * 100)}%</strong>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 16,
              overflow: "hidden",
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

