import React from "react";

function TransactionsTable({ transactions }) {
  if (!transactions || transactions.length === 0) {
    return <div style={{ fontSize: 13, color: "#9ca3af" }}>No data yet.</div>;
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Merchant</th>
            <th>Amount</th>
            <th>Category</th>
            <th>Source</th>
            <th>Recurring</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id}>
              <td>{tx.transaction_date}</td>
              <td>{tx.merchant || "—"}</td>
              <td>₹{tx.amount}</td>
              <td>{tx.category || "Other"}</td>
              <td>{tx.source_type}</td>
              <td>{tx.is_recurring ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TransactionsTable;

