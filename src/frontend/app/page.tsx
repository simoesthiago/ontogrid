import { getDatasets, getSources } from "../lib/api";
import { graphEntities } from "../lib/public-demo-data";

export default async function HomePage() {
  const [sourcesData, datasetsData] = await Promise.all([
    getSources(),
    getDatasets(),
  ]);

  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">Energy Data Hub</p>
          <h2>Baseline publico do OntoGrid</h2>
          <p className="muted">
            Catalogo de fontes, datasets e series publicas para ANEEL, ONS e CCEE.
            Dados curados, versionados e prontos para consumo via API REST.
          </p>
        </div>
        <div className="badge">REST-only public v1</div>
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
          <span className="muted">datasets no catalogo</span>
        </article>
        <article className="card">
          <p className="eyebrow">Graph</p>
          <strong>{graphEntities.length}</strong>
          <span className="muted">entidades publicas visiveis</span>
        </article>
      </div>

      <article className="card">
        <p className="eyebrow">Proximos passos</p>
        <ul className="list">
          <li>Materializar entidades, aliases e relacoes publicas em Neo4j.</li>
          <li>Persistir series temporais em TimescaleDB e expor via API.</li>
          <li>Acoplar o copiloto analitico a datasets, versoes e metadados.</li>
        </ul>
      </article>
    </section>
  );
}
