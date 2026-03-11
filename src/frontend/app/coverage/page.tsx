import { getCatalogCoverage } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function CoveragePage() {
  const data = await getCatalogCoverage();

  return (
    <section className="stack">
      <header className="hero">
        <div>
          <p className="eyebrow">Coverage</p>
          <h2>Inventario documental versus runtime real</h2>
          <p className="muted">
            Esta tela responde diretamente ao gap atual: o produto conhece centenas de
            datasets nos relatórios, mas só uma fração ainda tem pipeline de ingestão e
            publicação.
          </p>
        </div>
        <div className="badge">345 datasets mapeados</div>
      </header>

      <div className="grid three">
        <article className="card">
          <p className="eyebrow">Documented</p>
          <strong>{data.inventoried_total}</strong>
          <span className="muted">datasets inventariados</span>
        </article>
        <article className="card">
          <p className="eyebrow">Implemented</p>
          <strong>{data.adapter_enabled_total + data.published_total}</strong>
          <span className="muted">datasets com adapter</span>
        </article>
        <article className="card">
          <p className="eyebrow">Published</p>
          <strong>{data.published_total}</strong>
          <span className="muted">datasets com versao materializada</span>
        </article>
      </div>

      <section className="stack">
        <header>
          <p className="eyebrow">By Source</p>
          <h3>Onde esta o gap hoje</h3>
        </header>
        <div className="grid">
          {data.sources.map((source) => (
            <article key={source.source_code} className="card">
              <div className="row">
                <strong>{source.source_name}</strong>
                <span className="pill">{source.inventoried_total}</span>
              </div>
              <p className="muted">{source.source_document}</p>
              <p className="muted">
                {source.documented_only_total} documentados, {source.adapter_enabled_total} com
                adapter e {source.published_total} publicados.
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="stack">
        <header>
          <p className="eyebrow">By Family</p>
          <h3>Blocos tematicos para a ontologia</h3>
        </header>
        <div className="grid">
          {data.families.map((family) => (
            <article key={`${family.source_code}-${family.family}`} className="card">
              <div className="row">
                <strong>{family.family}</strong>
                <span className="pill">{family.inventoried_total}</span>
              </div>
              <p className="muted">{family.source_code}</p>
              <p className="muted">
                {family.documented_only_total} documentados, {family.adapter_enabled_total} em
                staging, {family.published_total} publicados.
              </p>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}
