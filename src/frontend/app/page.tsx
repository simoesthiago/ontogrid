import { datasetCards, graphEntities, sourceCards } from "../lib/public-demo-data";

export default function HomePage() {
  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">Energy Data Hub</p>
          <h2>Baseline publico do OntoGrid</h2>
          <p className="muted">
            O scaffold atual cobre catalogo de fontes, datasets, series publicas e um grafo
            inicial para ANEEL, ONS e CCEE.
          </p>
        </div>
        <div className="badge">REST-only public v1</div>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Sources</p>
          <strong>{sourceCards.length}</strong>
          <span className="muted">fontes publicas priorizadas</span>
        </article>
        <article className="card">
          <p className="eyebrow">Datasets</p>
          <strong>{datasetCards.length}</strong>
          <span className="muted">datasets demonstrativos no catalogo</span>
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
          <li>Trocar os mocks do catalogo por persistencia em PostgreSQL e TimescaleDB.</li>
          <li>Materializar entidades, aliases e relacoes publicas em Neo4j.</li>
          <li>Acoplar o copiloto analitico a datasets, versoes e metadados.</li>
        </ul>
      </article>
    </section>
  );
}
