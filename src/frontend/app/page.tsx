import Link from "next/link";

import {
  getCatalogCoverage,
  getDatasets,
  getGraphEntities,
  getInsightsOverview,
  getSources,
} from "../lib/api";

export const dynamic = "force-dynamic";

function formatNumber(value: number) {
  return value.toLocaleString("pt-BR", { maximumFractionDigits: 0 });
}

function formatMetric(value: number) {
  return value.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
}

export default async function HomePage() {
  const [sourcesData, datasetsData, coverageData, entitiesData, insightsData] = await Promise.all([
    getSources(),
    getDatasets(),
    getCatalogCoverage(),
    getGraphEntities({ limit: 12 }),
    getInsightsOverview(),
  ]);

  const activeSources = sourcesData.items.filter((item) => item.status === "active").length;
  const implementationTotal = coverageData.adapter_enabled_total + coverageData.published_total;
  const executionRate = coverageData.inventoried_total
    ? Math.round((implementationTotal / coverageData.inventoried_total) * 100)
    : 0;

  return (
    <section className="stack">
      <header className="hero heroMission">
        <div className="heroCopy">
          <p className="eyebrow">Energy Data Hub</p>
          <h2>Uma interface mais proxima de mission control do que de dashboard generico.</h2>
          <p className="muted heroLead">
            O OntoGrid precisa parecer um sistema de decisao: mais densidade informacional,
            hierarquia forte, estados claros, provenance visivel e navegacao pensada para
            operadores, analistas e times de produto.
          </p>
          <div className="heroActions">
            <Link href="/datasets" className="button">
              Explorar datasets
            </Link>
            <Link href="/graph" className="button buttonGhost">
              Abrir semantic layer
            </Link>
          </div>
        </div>

        <div className="heroAside">
          <article className="heroPanel">
            <p className="eyebrow">Runtime posture</p>
            <div className="metaGrid">
              <div>
                <strong>{formatNumber(sourcesData.total)}</strong>
                <p className="muted">sources catalogadas</p>
              </div>
              <div>
                <strong>{formatNumber(datasetsData.total)}</strong>
                <p className="muted">datasets navegaveis</p>
              </div>
              <div>
                <strong>{formatNumber(entitiesData.total)}</strong>
                <p className="muted">entities no grafo</p>
              </div>
              <div>
                <strong>{executionRate}%</strong>
                <p className="muted">pipeline execution rate</p>
              </div>
            </div>
          </article>
        </div>
      </header>

      <div className="grid four">
        <article className="card">
          <p className="eyebrow">Active sources</p>
          <strong>{formatNumber(activeSources)}</strong>
          <span className="muted">autoridades publicas em operacao</span>
        </article>
        <article className="card">
          <p className="eyebrow">Published versions</p>
          <strong>{formatNumber(coverageData.published_total)}</strong>
          <span className="muted">datasets com materializacao pronta para consumo</span>
        </article>
        <article className="card">
          <p className="eyebrow">Pipeline execution</p>
          <strong>{formatNumber(implementationTotal)}</strong>
          <span className="muted">adapters e publicacoes com runtime real</span>
        </article>
        <article className="card">
          <p className="eyebrow">Documentation gap</p>
          <strong>{formatNumber(coverageData.documented_only_total)}</strong>
          <span className="muted">datasets ainda fora da trilha executavel</span>
        </article>
      </div>

      <section className="grid dashboardSplit">
        <article className="card stack">
          <div className="row">
            <div>
              <p className="eyebrow">Source radar</p>
              <h3>Onde o hub esta realmente vivo</h3>
            </div>
            <span className="pill healthy">{executionRate}% executed</span>
          </div>

          {coverageData.sources.slice(0, 4).map((source) => {
            const sourceExecution = source.adapter_enabled_total + source.published_total;
            const percentage = source.inventoried_total
              ? Math.round((sourceExecution / source.inventoried_total) * 100)
              : 0;

            return (
              <div key={source.source_code} className="sourceTrack">
                <div className="row">
                  <div>
                    <strong>{source.source_name}</strong>
                    <p className="muted">{source.source_document}</p>
                  </div>
                  <span className={`pill ${percentage >= 60 ? "healthy" : percentage >= 30 ? "warning" : ""}`}>
                    {percentage}% live
                  </span>
                </div>
                <div className="progress">
                  <span style={{ width: `${Math.max(8, percentage)}%` }} />
                </div>
                <div className="row mutedMono">
                  <span>{formatNumber(source.inventoried_total)} mapped</span>
                  <span>{formatNumber(source.published_total)} published</span>
                </div>
              </div>
            );
          })}
        </article>

        <article className="card stack">
          <div>
            <p className="eyebrow">Control principles</p>
            <h3>O que faltava na UI anterior</h3>
          </div>
          <ul className="list">
            <li>Mais contraste e densidade para parecer software operacional, nao landing page.</li>
            <li>Hierarquia clara entre shell, contexto da pagina, metricas e trilha de acao.</li>
            <li>Tokens visuais para status, progressao, provenance e leitura de risco.</li>
            <li>Navegacao lateral com agrupamento funcional em vez de lista solta de links.</li>
          </ul>
          <div className="metaGrid">
            <div>
              <p className="eyebrow">Visual language</p>
              <strong>Industrial dark</strong>
            </div>
            <div>
              <p className="eyebrow">Signal bias</p>
              <strong>Operational clarity</strong>
            </div>
          </div>
        </article>
      </section>

      <section className="stack">
        <header>
          <p className="eyebrow">Signal board</p>
          <h3>Leituras analiticas que merecem destaque imediato</h3>
        </header>
        <div className="grid three">
          {insightsData.cards.map((card) => (
            <article key={card.id} className="card signalCard">
              <div className="row">
                <div>
                  <p className="eyebrow">{card.trend}</p>
                  <strong>{card.title}</strong>
                </div>
                <span className={`pill ${card.trend === "up" ? "warning" : card.trend === "down" ? "healthy" : ""}`}>
                  {card.unit}
                </span>
              </div>
              <p className="metric">{formatMetric(card.value)}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid dashboardSplit">
        <article className="card stack">
          <div className="row">
            <div>
              <p className="eyebrow">Graph frontier</p>
              <h3>Entidades com semantica pronta para exploracao</h3>
            </div>
            <Link href="/graph" className="button buttonGhost">
              Abrir graph
            </Link>
          </div>

          <div className="entityList">
            {entitiesData.items.slice(0, 6).map((entity) => (
              <Link key={entity.id} href={`/entities/${entity.id}`} className="entityRow">
                <div>
                  <strong>{entity.name}</strong>
                  <p className="muted">
                    {entity.canonical_code || "sem codigo canonico"} / {entity.jurisdiction}
                  </p>
                </div>
                <span className="pill">{entity.entity_type}</span>
              </Link>
            ))}
          </div>
        </article>

        <article className="card stack">
          <div>
            <p className="eyebrow">Grounded highlights</p>
            <h3>Ultimas leituras que conectam dataset e insight</h3>
          </div>
          <ul className="list">
            {insightsData.highlights.map((highlight) => (
              <li key={highlight.dataset_version_id}>{highlight.title}</li>
            ))}
          </ul>
        </article>
      </section>
    </section>
  );
}
