import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Bar, Pie } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

function CardWrapper({ title, children }) {
  return (
    <div
      style={{
        padding: 16,
        borderRadius: 12,
        background:
          "linear-gradient(145deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92))",
        border: "1px solid rgba(148,163,184,0.35)",
      }}
    >
      <div
        style={{ fontSize: 14, fontWeight: 500, marginBottom: 8, color: "#e5e7eb" }}
      >
        {title}
      </div>
      <div style={{ height: 220 }}>{children}</div>
    </div>
  );
}

export default function AnalyticsCharts({ graphs }) {
  if (!graphs) return null;

  const spending30 = graphs.spending_last_30_days || [];
  const catDist = graphs.category_distribution || [];
  const weekly = graphs.weekly_spending_comparison || [];
  const burnTrend = graphs.burn_rate_trend || [];
  const survival = graphs.survival_forecast || [];

  const line30Data = {
    labels: spending30.map((d) => d.date.slice(5)),
    datasets: [
      {
        label: "Spend",
        data: spending30.map((d) => d.amount),
        borderColor: "#22c55e",
        backgroundColor: "rgba(34,197,94,0.2)",
        tension: 0.35,
      },
    ],
  };

  const catData = {
    labels: catDist.map((c) => c.category),
    datasets: [
      {
        data: catDist.map((c) => c.amount),
        backgroundColor: [
          "#22c55e",
          "#0ea5e9",
          "#a855f7",
          "#f97316",
          "#ef4444",
          "#14b8a6",
        ],
      },
    ],
  };

  const weeklyData = {
    labels: weekly.map((w) => w.week_start.slice(5)),
    datasets: [
      {
        label: "Weekly Spend",
        data: weekly.map((w) => w.amount),
        backgroundColor: "rgba(59,130,246,0.65)",
      },
    ],
  };

  const burnData = {
    labels: burnTrend.map((b) => b.week_start.slice(5)),
    datasets: [
      {
        label: "Burn Rate (₹/mo)",
        data: burnTrend.map((b) => b.burn_rate),
        borderColor: "#f97316",
        backgroundColor: "rgba(249,115,22,0.25)",
        tension: 0.3,
      },
    ],
  };

  const survivalData = {
    labels: survival.map((s) => s.date.slice(5)),
    datasets: [
      {
        label: "Projected Balance",
        data: survival.map((s) => s.projected_balance),
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56,189,248,0.2)",
        tension: 0.25,
      },
    ],
  };

  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: "#9ca3af",
        },
      },
      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
    scales: {
      x: {
        ticks: { color: "#6b7280", maxRotation: 0, minRotation: 0 },
        grid: { color: "rgba(31,41,55,0.6)" },
      },
      y: {
        ticks: { color: "#6b7280" },
        grid: { color: "rgba(31,41,55,0.6)" },
      },
    },
  };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(0,2fr) minmax(0,1.3fr)",
        gap: 16,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <CardWrapper title="Spending – Last 30 Days">
          <Line data={line30Data} options={baseOptions} />
        </CardWrapper>
        <CardWrapper title="Weekly Spending Comparison">
          <Bar data={weeklyData} options={baseOptions} />
        </CardWrapper>
        <CardWrapper title="Survival Days Forecast (Balance)">
          <Line data={survivalData} options={baseOptions} />
        </CardWrapper>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <CardWrapper title="Category Distribution">
          <Pie
            data={catData}
            options={{
              plugins: {
                legend: {
                  position: "bottom",
                  labels: { color: "#9ca3af" },
                },
              },
            }}
          />
        </CardWrapper>
        <CardWrapper title="Burn Rate Trend">
          <Line data={burnData} options={baseOptions} />
        </CardWrapper>
      </div>
    </div>
  );
}

