import { getSources } from "../../lib/api";

export default async function SourcesPage() {
  const data = await getSources();

  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Sources</p>
        <h2>Fontes publicas priorizadas</h2>
        <p className="muted">Curadoria inicial do hub publico com ANEEL, ONS e CCEE.</p>
      </header>
      <div className="grid">
        {data.items.map((source) => (
          <article key={source.id} className="card">
            <div className="row">
              <strong>{source.name}</strong>
              <span className={`pill ${source.status === "active" ? "healthy" : ""}`}>
                {source.status}
              </span>
            </div>
            <p className="muted">{source.authority_type}</p>
            <p>{source.refresh_strategy}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
