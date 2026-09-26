import React from "react";

export default function Privacy() {
  return (
    <main className="page legal-page">
      <section className="page-heading">
        <span className="eyebrow">privacy</span>
        <h1>How this demo handles data</h1>
      </section>
      <div className="legal-copy">
        <p>PayCom is a demonstration store. We do not ask for accounts, names, addresses, or marketing consent in this app.</p>
        <h2>Data we process</h2>
        <p>The backend stores the catalog cart and order records needed to demonstrate checkout. Razorpay receives payment details directly through its checkout flow; this app does not store card or bank information.</p>
        <h2>Important limitation</h2>
        <p>The demo cart is shared by visitors and is not suitable for real customers until session or account-based cart ownership is implemented. Do not use real personal or payment data in this deployment.</p>
        <h2>Retention and requests</h2>
        <p>Deployment operators are responsible for database retention, backups, access control, and responding to data requests. Contact the store operator to request correction or deletion of stored demo order data.</p>
      </div>
    </main>
  );
}