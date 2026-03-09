import { graphEntities } from "../../lib/public-demo-data";

export default function GraphPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Graph</p>
        <h2>Entidades publicas do setor</h2>
        <p className="muted">O grafo publico conecta submercados, agentes e datasets versionados.</p>
      </header>
      <div className="grid">
        {graphEntities.map((entity) => (
          <article key={entity.id} className="card">
            <div className="row">
              <strong>{entity.name}</strong>
              <span className="pill">{entity.type}</span>
            </div>
            <p className="muted">Fonte: {entity.source}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
