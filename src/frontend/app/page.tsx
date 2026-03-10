import {
  getCatalogCoverage,
  getDatasets,
  getGraphEntities,
  getInsightsOverview,
  getSources,
} from "../lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [sourcesData, datasetsData, coverageData, entitiesData, insightsData] = await Promise.all([
    getSources(),
    getDatasets(),
    getCatalogCoverage(),
    getGraphEntities({ limit: 12 }),
    getInsightsOverview(),
  ]);

  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">Energy Data Hub</p>
          <h2>Hub publico com catalogo, semantica e series rastreaveis</h2>
          <p className="muted">
            O runtime oficial agora parte de uma stack local com FastAPI, TimescaleDB,
            Neo4j e Redis. O frontend ja consome catalogo, grafo e insights reais.
          </p>
        </div>
        <div className="badge">Docker compose dev runtime</div>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Sources</p>
          <strong>{sourcesData.total}</strong>
          <span className="muted">fontes publicas ativas</span>
        </article>
        <article className="card">
          <p className="eyebrow">Datasets</p>
          <strong>{datasetsData.total}</strong>
          <span className="muted">datasets inventariados no catalogo</span>
        </article>
        <article className="card">
          <p className="eyebrow">Entities</p>
          <strong>{entitiesData.total}</strong>
          <span className="muted">entidades canonicas materializadas</span>
        </article>
      </div>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Published</p>
          <strong>{coverageData.published_total}</strong>
          <span className="muted">datasets com versao publicada</span>
        </article>
        <article className="card">
          <p className="eyebrow">Adapters</p>
          <strong>{coverageData.adapter_enabled_total + coverageData.published_total}</strong>
          <span className="muted">datasets com pipeline implementado</span>
        </article>
        <article className="card">
          <p className="eyebrow">Gap</p>
          <strong>{coverageData.documented_only_total}</strong>
          <span className="muted">datasets so documentados hoje</span>
        </article>
      </div>

      <section className="stack">
        <header>
          <p className="eyebrow">Overview</p>
          <h3>Leituras analiticas das ultimas publicacoes</h3>
        </header>
        <div className="grid three">
          {insightsData.cards.map((card) => (
            <article key={card.id} className="card">
              <p className="eyebrow">{card.trend}</p>
              <strong>{card.title}</strong>
              <p className="metric">
                {card.value.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}
              </p>
              <p className="muted">{card.unit}</p>
            </article>
          ))}
        </div>
      </section>

      <article className="card">
        <p className="eyebrow">Highlights</p>
        <ul className="list">
          {insightsData.highlights.map((highlight) => (
            <li key={highlight.dataset_version_id}>{highlight.title}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}
