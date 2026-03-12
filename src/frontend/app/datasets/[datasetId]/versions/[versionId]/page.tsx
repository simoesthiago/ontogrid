import Link from "next/link";

import {
  getDataset,
  getDatasetVersion,
  getSeries,
  getSeriesObservations,
} from "../../../../../lib/api";

export const dynamic = "force-dynamic";

function renderLineage(lineage: Record<string, unknown>) {
  return Object.entries(lineage);
}

export default async function DatasetVersionPage({
  params,
}: {
  params: Promise<{ datasetId: string; versionId: string }>;
}) {
  const { datasetId, versionId } = await params;
  const [dataset, version, series] = await Promise.all([
    getDataset(datasetId),
    getDatasetVersion(datasetId, versionId),
    getSeries({ dataset_id: datasetId, limit: 12 }),
  ]);

  const observationBySeries = await Promise.all(
    series.items.slice(0, 6).map(async (item) => ({
      series: item,
      observations: await getSeriesObservations(item.id, {
        dataset_version_id: versionId,
        limit: 8,
      }),
    })),
  );

  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">{dataset.code}</p>
          <h2>Versao {version.label}</h2>
          <p className="muted">{dataset.name}</p>
        </div>
        <div className="badge">{version.status}</div>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Published</p>
          <strong>{version.published_at}</strong>
          <p className="muted">extraido em {version.extracted_at}</p>
        </article>
        <article className="card">
          <p className="eyebrow">Rows</p>
          <strong>{version.row_count}</strong>
          <p className="muted">schema {version.schema_version}</p>
        </article>
        <article className="card">
          <p className="eyebrow">Coverage</p>
          <strong>{version.coverage_start || "n/a"}</strong>
          <p className="muted">ate {version.coverage_end || "n/a"}</p>
        </article>
      </div>

      <article className="card stack">
        <div className="row">
          <strong>Lineage</strong>
          <Link href={`/datasets/${datasetId}`}>voltar ao dataset</Link>
        </div>
        <ul className="list">
          {renderLineage(version.lineage).map(([key, value]) => (
            <li key={key}>
              {key}: {String(value)}
            </li>
          ))}
        </ul>
      </article>

      <section className="stack">
        <header>
          <p className="eyebrow">Observations</p>
          <h3>Observacoes desta versao por serie</h3>
        </header>
        <div className="grid">
          {observationBySeries.length ? (
            observationBySeries.map(({ series: item, observations }) => (
              <article key={item.id} className="card stack">
                <div className="row">
                  <strong>{item.metric_name}</strong>
                  <span className="pill">{item.semantic_value_type}</span>
                </div>
                <p className="muted">{item.metric_code}</p>
                <ul className="list">
                  {observations.items.length ? (
                    observations.items.map((observation) => (
                      <li key={`${item.id}-${observation.entity_id}-${observation.timestamp}`}>
                        <Link href={`/entities/${observation.entity_id}`}>{observation.entity_name}</Link>
                        {" - "}
                        {String(observation.value)} {observation.unit} em {observation.timestamp}
                      </li>
                    ))
                  ) : (
                    <li>Sem observacoes para esta serie nesta versao.</li>
                  )}
                </ul>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Nenhuma serie encontrada para este dataset.</p>
            </article>
          )}
        </div>
      </section>
    </section>
  );
}
