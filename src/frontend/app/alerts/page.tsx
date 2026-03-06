import { alerts } from "../../lib/demo-data";

export default function AlertsPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Alerts</p>
        <h2>Painel de alertas</h2>
      </header>
      <div className="grid">
        {alerts.map((alert) => (
          <article key={alert.id} className="card">
            <div className="row">
              <strong>{alert.title}</strong>
              <span className={`pill ${alert.severity}`}>{alert.severity}</span>
            </div>
            <p className="muted">{alert.asset}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
