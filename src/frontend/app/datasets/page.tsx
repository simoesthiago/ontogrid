import { getCatalogCoverage, getDatasets } from "../../lib/api";

export const dynamic = "force-dynamic";

const statusMeta: Record<string, { label: string; className: string }> = {
  published: { label: "published", className: "healthy" },
  adapter_enabled: { label: "adapter", className: "warning" },
  documented_only: { label: "documented", className: "" },
};

export default async function DatasetsPage() {
  const [data, coverage] = await Promise.all([
    getDatasets({ limit: 400 }),
    getCatalogCoverage(),
  ]);

  const datasetsBySource = new Map<string, typeof data.items>();
  for (const item of data.items) {
    const existing = datasetsBySource.get(item.source_code) ?? [];
    existing.push(item);
    datasetsBySource.set(item.source_code, existing);
  }

  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Datasets</p>
        <h2>Universo documentado do Energy Data Hub</h2>
        <p className="muted">
          O catalogo agora reflete os inventarios de ANEEL, ONS e CCEE. O status de cada
          dataset deixa claro se ele esta apenas documentado, se ja tem adapter ou se ja
          publica versoes no runtime.
        </p>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Inventoried</p>
          <strong>{coverage.inventoried_total}</strong>
          <span className="muted">datasets mapeados nos documentos</span>
        </article>
        <article className="card">
          <p className="eyebrow">Implemented</p>
          <strong>{coverage.adapter_enabled_total + coverage.published_total}</strong>
          <span className="muted">datasets com pipeline real</span>
        </article>
        <article className="card">
          <p className="eyebrow">Published</p>
          <strong>{coverage.published_total}</strong>
          <span className="muted">datasets com versao carregada</span>
        </article>
      </div>

      {coverage.sources.map((source) => {
        const items = datasetsBySource.get(source.source_code) ?? [];
        return (
          <section key={source.source_code} className="stack">
            <article className="card">
              <div className="row">
                <div>
                  <p className="eyebrow">{source.source_code}</p>
                  <h3>{source.source_name}</h3>
                </div>
                <span className="pill">{source.inventoried_total} datasets</span>
              </div>
              <p className="muted">{source.source_document}</p>
              <div className="grid three">
                <div>
                  <strong>{source.documented_only_total}</strong>
                  <p className="muted">so documentados</p>
                </div>
                <div>
                  <strong>{source.adapter_enabled_total}</strong>
                  <p className="muted">com adapter sem publicacao</p>
                </div>
                <div>
                  <strong>{source.published_total}</strong>
                  <p className="muted">publicados</p>
                </div>
              </div>
            </article>

            <div className="grid">
              {items.map((dataset) => {
                const status = statusMeta[dataset.ingestion_status] ?? statusMeta.documented_only;
                return (
                  <article key={dataset.id} className="card">
                    <div className="row">
                      <strong>{dataset.name}</strong>
                      <span className={`pill ${status.className}`}>{status.label}</span>
                    </div>
                    <p className="muted">{dataset.code}</p>
                    <p>{dataset.domain}</p>
                    <p className="muted">Granularidade: {dataset.granularity}</p>
                    <p className="muted">
                      {dataset.latest_version
                        ? `Ultima versao: ${dataset.latest_version}`
                        : "Sem versao publicada"}
                    </p>
                  </article>
                );
              })}
            </div>
          </section>
        );
      })}
    </section>
  );
}
