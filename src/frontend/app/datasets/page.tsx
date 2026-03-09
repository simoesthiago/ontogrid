import { datasetCards } from "../../lib/public-demo-data";

export default function DatasetsPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Datasets</p>
        <h2>Catalogo inicial do Energy Data Hub</h2>
        <p className="muted">Cada dataset combina fonte, dominio, granularidade e versao publicada.</p>
      </header>
      <div className="grid">
        {datasetCards.map((dataset) => (
          <article key={dataset.id} className="card">
            <div className="row">
              <strong>{dataset.name}</strong>
              <span className="pill">{dataset.version}</span>
            </div>
            <p className="muted">{dataset.source}</p>
            <p>{dataset.domain}</p>
            <p className="muted">Granularidade: {dataset.granularity}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
