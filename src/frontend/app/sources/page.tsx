import { sourceCards } from "../../lib/public-demo-data";

export default function SourcesPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Sources</p>
        <h2>Fontes publicas priorizadas</h2>
        <p className="muted">Curadoria inicial do hub publico com ANEEL, ONS e CCEE.</p>
      </header>
      <div className="grid">
        {sourceCards.map((source) => (
          <article key={source.id} className="card">
            <div className="row">
              <strong>{source.name}</strong>
              <span className="pill healthy">{source.status}</span>
            </div>
            <p className="muted">{source.type}</p>
            <p>{source.strategy}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
