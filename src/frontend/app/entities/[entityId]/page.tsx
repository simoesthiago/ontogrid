import {
  type EntityProfileEvidenceItem,
  type EntityProfileResponse,
  getEntityProfile,
} from "../../../lib/api";

export const dynamic = "force-dynamic";

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "n/a";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatValue(item)).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, item]) => `${key}: ${formatValue(item)}`)
      .join(" / ");
  }
  return String(value);
}

function labeledCard(label: string, value: string, detail: string) {
  return (
    <article className="card" key={label}>
      <p className="eyebrow">{label}</p>
      <strong>{value}</strong>
      <p className="muted">{detail}</p>
    </article>
  );
}

function renderObjectLens(profile: EntityProfileResponse) {
  const generationAsset = profile.facets.generation_asset as Record<string, unknown> | null | undefined;
  const party = profile.facets.party as Record<string, unknown> | null | undefined;
  const geo = profile.facets.geo ?? [];
  const regulatory = profile.facets.regulatory as Record<string, unknown> | null | undefined;

  if (profile.identity.entity_type === "submarket") {
    const trackedSeries = profile.series
      .map((item) => `${item.metric_name} (${item.semantic_value_type})`)
      .slice(0, 3)
      .join(" / ");
    return (
      <div className="grid three">
        {labeledCard("Scope", profile.identity.jurisdiction, "jurisdicao eletrica do objeto")}
        {labeledCard("Series", String(profile.series.length), trackedSeries || "sem series publicadas")}
        {labeledCard(
          "Neighbors",
          String(profile.neighbors?.edges.length ?? 0),
          "arestas projetadas no grafo publico",
        )}
      </div>
    );
  }

  if (profile.identity.entity_type === "plant" && generationAsset) {
    const bridges = Array.isArray(generationAsset.bridge_codes)
      ? String((generationAsset.bridge_codes as unknown[]).length)
      : "0";
    return (
      <div className="grid three">
        {labeledCard("CEG", formatValue(generationAsset.ceg), "identificador canonicamente reconciliado")}
        {labeledCard("ONS", formatValue(generationAsset.ons_plant_code), "codigo operacional publicado")}
        {labeledCard("Bridges", bridges, "codigos publicos reconciliados entre fontes")}
      </div>
    );
  }

  if (profile.identity.entity_type === "agent" && party) {
    return (
      <div className="grid three">
        {labeledCard("Tax ID", formatValue(party.tax_id), "identidade legal usada no match publico")}
        {labeledCard("Profiles", String(profile.facets.agent_profile.length), "facetas regulatoria e de mercado")}
        {labeledCard("Datasets", String(profile.recent_versions.length), "versoes recentes associadas ao agente")}
      </div>
    );
  }

  if (profile.identity.entity_type === "distributor") {
    const trackedMetrics = Array.isArray(regulatory?.tracked_metrics)
      ? (regulatory?.tracked_metrics as unknown[]).length
      : 0;
    return (
      <div className="grid three">
        {labeledCard("Tariffs+Quality", String(trackedMetrics), "metricas regulatorias publicadas")}
        {labeledCard("Coverage", String(geo.length), "mapeamentos geograficos e eletricos")}
        {labeledCard("Evidence", String(profile.evidence.length), "claims rastreaveis publicados")}
      </div>
    );
  }

  return (
    <div className="grid three">
      {labeledCard("Aliases", String(profile.aliases.length), "identificadores reconciliados")}
      {labeledCard("Series", String(profile.series.length), "series semanticamente tipadas")}
      {labeledCard("Evidence", String(profile.evidence.length), "evidencias publicas disponiveis")}
    </div>
  );
}

function renderEvidenceDetail(evidence: EntityProfileEvidenceItem) {
  const parts = Object.entries(evidence.selector ?? {})
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${formatValue(value)}`);
  return parts.join(" / ");
}

export default async function EntityProfilePage({
  params,
}: {
  params: Promise<{ entityId: string }>;
}) {
  const { entityId } = await params;
  const profile = await getEntityProfile(entityId);
  const party = profile.facets.party as Record<string, unknown> | null | undefined;
  const generationAsset = profile.facets.generation_asset as Record<string, unknown> | null | undefined;
  const regulatory = profile.facets.regulatory as Record<string, unknown> | null | undefined;

  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">{profile.semantic_type}</p>
          <h2>{profile.identity.name}</h2>
          <p className="muted">
            {profile.identity.canonical_code || "Sem codigo canonico"} / Jurisdicao {profile.identity.jurisdiction}
          </p>
        </div>
        <div className="badge">{profile.graph_status === "available" ? "Graph online" : "Graph partial"}</div>
      </header>

      {renderObjectLens(profile)}

      <div className="grid">
        <article className="card">
          <p className="eyebrow">Identity</p>
          <strong>{profile.identity.entity_type}</strong>
          <p className="muted">
            {Object.entries(profile.identity.attributes)
              .slice(0, 4)
              .map(([key, value]) => `${key}: ${formatValue(value)}`)
              .join(" / ") || "sem atributos canonicamente publicados"}
          </p>
        </article>

        <article className="card">
          <p className="eyebrow">Party</p>
          {party ? (
            <>
              <strong>{formatValue(party.legal_name || profile.identity.name)}</strong>
              <p className="muted">{formatValue(party.tax_id)}</p>
              <p className="muted">{formatValue(party.status)}</p>
            </>
          ) : (
            <p className="muted">Sem faceta party para esta entidade.</p>
          )}
        </article>

        <article className="card">
          <p className="eyebrow">Aliases</p>
          <ul className="list">
            {profile.aliases.length ? (
              profile.aliases.map((alias) => (
                <li key={`${alias.source_code}-${alias.alias_name}`}>
                  {alias.alias_name} ({alias.source_code})
                </li>
              ))
            ) : (
              <li>Sem aliases publicados.</li>
            )}
          </ul>
        </article>
      </div>

      {generationAsset ? (
        <article className="card">
          <p className="eyebrow">Generation Asset</p>
          <div className="grid three">
            <div>
              <strong>{formatValue(generationAsset.ceg)}</strong>
              <p className="muted">CEG</p>
            </div>
            <div>
              <strong>{formatValue(generationAsset.source_type)}</strong>
              <p className="muted">Fonte</p>
            </div>
            <div>
              <strong>{formatValue(generationAsset.installed_capacity_mw)}</strong>
              <p className="muted">MW instalados</p>
            </div>
          </div>
        </article>
      ) : null}

      {profile.facets.agent_profile.length ? (
        <section className="stack">
          <header>
            <p className="eyebrow">Profiles</p>
            <h3>Facetas regulatoria e de mercado</h3>
          </header>
          <div className="grid">
            {profile.facets.agent_profile.map((item, index) => (
              <article key={`${item.profile_kind}-${item.role}-${index}`} className="card">
                <strong>{formatValue(item.role)}</strong>
                <p className="muted">{formatValue(item.profile_kind)}</p>
                <p className="muted">
                  {formatValue(item.source_code)} / {formatValue(item.external_code)}
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {profile.facets.geo.length ? (
        <section className="stack">
          <header>
            <p className="eyebrow">Geo</p>
            <h3>Mapeamentos geografico-eletricos</h3>
          </header>
          <div className="grid">
            {profile.facets.geo.map((item, index) => (
              <article key={`${item.geo_type}-${index}`} className="card">
                <strong>{formatValue(item.geo_type)}</strong>
                <p className="muted">{formatValue(item.ibge_code || item.operator_code)}</p>
                <p className="muted">
                  parent {formatValue(item.parent_entity_id)} / mapped {formatValue(item.mapped_entity_id)}
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {regulatory ? (
        <article className="card">
          <p className="eyebrow">Regulatory</p>
          <p className="muted">
            {Object.entries(regulatory)
              .map(([key, value]) => `${key}: ${formatValue(value)}`)
              .join(" / ")}
          </p>
        </article>
      ) : null}

      <section className="stack">
        <header>
          <p className="eyebrow">Series</p>
          <h3>Ultimas series da entidade</h3>
        </header>
        <div className="grid">
          {profile.series.length ? (
            profile.series.map((series) => (
              <article key={series.series_id} className="card">
                <div className="row">
                  <strong>{series.metric_name}</strong>
                  <span className="pill">{series.semantic_value_type}</span>
                </div>
                <p className="muted">{series.dataset_code}</p>
                <p>
                  {formatValue(series.latest_value)} {series.unit}
                </p>
                <p className="muted">
                  {series.reference_time_kind} / {series.latest_observation_at}
                </p>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Esta entidade ainda nao possui serie temporal publicada.</p>
            </article>
          )}
        </div>
      </section>

      <section className="stack">
        <header>
          <p className="eyebrow">Recent Versions</p>
          <h3>Datasets que sustentam este objeto</h3>
        </header>
        <div className="grid">
          {profile.recent_versions.length ? (
            profile.recent_versions.map((version) => (
              <article key={version.dataset_version_id} className="card">
                <strong>{version.dataset_code}</strong>
                <p className="muted">{version.label}</p>
                <p className="muted">{version.published_at || "Sem published_at"}</p>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Nenhuma versao recente foi materializada para este objeto.</p>
            </article>
          )}
        </div>
      </section>

      <section className="stack">
        <header>
          <p className="eyebrow">Evidence</p>
          <h3>Grounding publicado</h3>
        </header>
        <div className="grid">
          {profile.evidence.length ? (
            profile.evidence.map((evidence) => (
              <article key={evidence.id} className="card">
                <p className="eyebrow">{evidence.scope_type}</p>
                <strong>{evidence.claim_text}</strong>
                <p className="muted">{evidence.dataset_version_id}</p>
                <p className="muted">{renderEvidenceDetail(evidence) || evidence.scope_id}</p>
              </article>
            ))
          ) : (
            <article className="card">
              <p className="muted">Sem evidencia publicada para este objeto.</p>
            </article>
          )}
        </div>
      </section>

      {profile.neighbors ? (
        <article className="card">
          <p className="eyebrow">Graph</p>
          <strong>{profile.neighbors.nodes.length} nos</strong>
          <p className="muted">
            {profile.neighbors.edges.length} arestas /{" "}
            {profile.neighbors.provenance.dataset_version_ids.length} versoes de dataset
          </p>
        </article>
      ) : null}
    </section>
  );
}
