import { getInsightsOverview } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function InsightsPage() {
  const data = await getInsightsOverview();

  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Insights</p>
        <h2>Snapshots analiticos grounded</h2>
        <p className="muted">
          O endpoint agora devolve cards e highlights derivados das ultimas publicacoes
          versionadas do hub.
        </p>
      </header>

      <div className="grid three">
        {data.cards.map((item) => (
          <article key={item.id} className="card">
            <div className="row">
              <strong>{item.title}</strong>
              <span className={`pill ${item.trend === "up" ? "warning" : item.trend === "down" ? "healthy" : ""}`}>
                {item.trend}
              </span>
            </div>
            <p className="metric">
              {item.value.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}
            </p>
            <p className="muted">{item.unit}</p>
          </article>
        ))}
      </div>

      <article className="card">
        <p className="eyebrow">Highlights</p>
        <ul className="list">
          {data.highlights.map((item) => (
            <li key={item.dataset_version_id}>{item.title}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}
