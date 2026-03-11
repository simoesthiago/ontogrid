import Link from "next/link";
import { getEntityNeighbors, getGraphEntities } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function GraphPage() {
  const entities = await getGraphEntities({ limit: 12 });
  const leadEntity = entities.items[0];
  const neighbors = leadEntity ? await getEntityNeighbors(leadEntity.id) : null;

  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Graph</p>
        <h2>Entidades canonicas do setor</h2>
        <p className="muted">
          A camada semantica agora sai de dados persistidos, com aliases reconciliados e
          proveniencia por dataset version.
        </p>
      </header>

      {neighbors ? (
        <article className="card">
          <p className="eyebrow">Vizinhança real</p>
          <strong>{leadEntity.name}</strong>
          <p className="muted">
            {neighbors.nodes.length} nos, {neighbors.edges.length} arestas e{" "}
            {neighbors.provenance.dataset_version_ids.length} versoes de dataset na trilha.
          </p>
        </article>
      ) : null}

      <div className="grid">
        {entities.items.map((entity) => (
          <article key={entity.id} className="card">
            <div className="row">
              <Link href={`/entities/${entity.id}`}>
                <strong>{entity.name}</strong>
              </Link>
              <span className="pill">{entity.entity_type}</span>
            </div>
            <p className="muted">{entity.canonical_code || "sem codigo canonico"}</p>
            <p className="muted">Jurisdicao: {entity.jurisdiction}</p>
            <p>{entity.aliases.join(", ") || "Sem aliases adicionais"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
