import { alerts, assetCards, cases } from "../lib/demo-data";

export default function HomePage() {
  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">Asset Health</p>
          <h2>Baseline codável do OntoGrid</h2>
          <p className="muted">
            O scaffold atual cobre cadastro de ativos, ingestão em lote, health score, alertas,
            casos simples e Energy Graph básico.
          </p>
        </div>
        <div className="badge">REST-only v0.1</div>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Assets</p>
          <strong>{assetCards.length}</strong>
          <span className="muted">ativos no exemplo local</span>
        </article>
        <article className="card">
          <p className="eyebrow">Alerts</p>
          <strong>{alerts.length}</strong>
          <span className="muted">alertas visíveis por polling</span>
        </article>
        <article className="card">
          <p className="eyebrow">Cases</p>
          <strong>{cases.length}</strong>
          <span className="muted">casos simples a partir de alertas</span>
        </article>
      </div>

      <article className="card">
        <p className="eyebrow">Próximos passos</p>
        <ul className="list">
          <li>Trocar o store em memória do backend por PostgreSQL/TimescaleDB.</li>
          <li>Persistir health score e alertas com regras reais por tipo de ativo.</li>
          <li>Sincronizar a topologia básica do Energy Graph com Neo4j.</li>
        </ul>
      </article>
    </section>
  );
}
