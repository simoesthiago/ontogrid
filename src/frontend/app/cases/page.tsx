import { cases } from "../../lib/demo-data";

export default function CasesPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Cases</p>
        <h2>Casos simples</h2>
      </header>
      <div className="grid">
        {cases.map((item) => (
          <article key={item.id} className="card">
            <div className="row">
              <strong>{item.title}</strong>
              <span className="pill warning">{item.priority}</span>
            </div>
            <p className="muted">{item.status}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
