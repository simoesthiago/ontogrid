import { getDatasets } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function DatasetsPage() {
  const data = await getDatasets();

  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Datasets</p>
        <h2>Catalogo inicial do Energy Data Hub</h2>
        <p className="muted">Cada dataset combina fonte, dominio, granularidade e versao publicada.</p>
      </header>
      <div className="grid">
        {data.items.map((dataset) => (
          <article key={dataset.id} className="card">
            <div className="row">
              <strong>{dataset.name}</strong>
              <span className={`pill ${dataset.freshness_status === "fresh" ? "healthy" : "warning"}`}>
                {dataset.latest_version}
              </span>
            </div>
            <p className="muted">{dataset.source_code}</p>
            <p>{dataset.domain}</p>
            <p className="muted">Granularidade: {dataset.granularity}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
