import Link from "next/link";

import {
  getDataset,
  getDatasetVersions,
  getRefreshJobs,
  getSeries,
  getSeriesObservations,
} from "../../../lib/api";

export const dynamic = "force-dynamic";

function renderSchemaSummary(summary: Record<string, unknown>) {
  return Object.entries(summary)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`)
    .join(" / ");
}

export default async function DatasetDetailPage({
  params,
}: {
  params: Promise<{ datasetId: string }>;
}) {
  const { datasetId } = await params;
  const [dataset, versions, series, refreshJobs] = await Promise.all([
    getDataset(datasetId),
    getDatasetVersions(datasetId),
    getSeries({ dataset_id: datasetId, limit: 12 }),
    getRefreshJobs({ dataset_id: datasetId, limit: 10 }),
  ]);

  const observationBySeries = await Promise.all(
    series.items.slice(0, 6).map(async (item) => ({
      series: item,
      observations: await getSeriesObservations(item.id, { limit: 8 }),
    })),
  );

  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">{dataset.source_code}</p>
          <h2>{dataset.name}</h2>
          <p className="muted">{dataset.code}</p>
          <p>{dataset.description}</p>
        </div>
        <div className="badge">{dataset.ingestion_status}</div>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Granularity</p>
          <strong>{dataset.granularity}</strong>
          <p className="muted">{dataset.domain}</p>
        </article>
        <article className="card">
          <p className="eyebrow">Refresh</p>
          <strong>{dataset.refresh_frequency}</strong>
          <p className="muted">
            {dataset.latest_version.label
              ? `ultima versao ${dataset.latest_version.label}`
              : "sem versao publicada"}
          </p>
        </article>
        <article className="card">
          <p className="eyebrow">Schema</p>
          <strong>{series.total} series</strong>
          <p className="muted">{renderSchemaSummary(dataset.schema_summary) || "sem resumo tipado"}</p>
        </article>
      </div>

      <section className="stack">
        <header>
          <p className="eyebrow">Versions</p>
          <h3>Versoes navegaveis do dataset</h3>
        </header>
        <div className="grid">
          {versions.items.length ? (
            versions.items.map((version) => (
              <article key={version.id} className="card">
                <div className="row">
                  <Link href={`/datasets/${dataset.id}/versions/${version.id}`}>
                    <strong>{version.label}</strong>
                  </Link>
                  <span className="pill">{version.status}</span>
                </div>
                <p className="muted">{version.published_at}</p>
                <p className="muted">
                  cobertura {version.coverage_start || "n/a"} ate {version.coverage_end || "n/a"}
                </p>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Nenhuma versao foi publicada para este dataset.</p>
            </article>
          )}
        </div>
      </section>

      <section className="stack">
        <header>
          <p className="eyebrow">Series</p>
          <h3>Series e observacoes recentes</h3>
        </header>
        <div className="grid">
          {observationBySeries.length ? (
            observationBySeries.map(({ series: item, observations }) => (
              <article key={item.id} className="card stack">
                <div className="row">
                  <strong>{item.metric_name}</strong>
                  <span className="pill">{item.semantic_value_type}</span>
                </div>
                <p className="muted">
                  {item.metric_code} / {item.reference_time_kind} / {item.temporal_granularity}
                </p>
                <ul className="list">
                  {observations.items.length ? (
                    observations.items.map((observation) => (
                      <li key={`${observation.entity_id}-${observation.timestamp}`}>
                        <Link href={`/entities/${observation.entity_id}`}>{observation.entity_name}</Link>
                        {" - "}
                        {String(observation.value)} {observation.unit} em {observation.timestamp}
                      </li>
                    ))
                  ) : (
                    <li>Sem observacoes publicadas.</li>
                  )}
                </ul>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Nenhuma serie foi registrada para este dataset.</p>
            </article>
          )}
        </div>
      </section>

      <section className="stack">
        <header>
          <p className="eyebrow">Refresh Jobs</p>
          <h3>Observabilidade minima do pipeline</h3>
        </header>
        <div className="grid">
          {refreshJobs.items.length ? (
            refreshJobs.items.map((job) => (
              <article key={job.id} className="card">
                <div className="row">
                  <strong>{job.status}</strong>
                  <span className="pill">{job.trigger_type}</span>
                </div>
                <p className="muted">{job.created_at}</p>
                <p className="muted">
                  leitura {job.rows_read} / escrita {job.rows_written}
                </p>
                <p className="muted">
                  {job.published_version_label
                    ? `versao publicada ${job.published_version_label}`
                    : job.error_summary || "sem versao publicada"}
                </p>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Nenhum refresh job foi registrado para este dataset.</p>
            </article>
          )}
        </div>
      </section>
    </section>
  );
}
