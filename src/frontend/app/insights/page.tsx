import { insightCards } from "../../lib/public-demo-data";

export default function InsightsPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Insights</p>
        <h2>Leituras iniciais sobre o acervo publico</h2>
        <p className="muted">Espaco reservado para snapshots analiticos e copiloto grounded.</p>
      </header>
      <div className="grid">
        {insightCards.map((item) => (
          <article key={item.title} className="card">
            <strong>{item.title}</strong>
            <p className="muted">{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
