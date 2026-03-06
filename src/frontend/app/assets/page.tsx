import { assetCards } from "../../lib/demo-data";

export default function AssetsPage() {
  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Assets</p>
        <h2>Lista inicial de ativos</h2>
      </header>
      <div className="grid">
        {assetCards.map((asset) => (
          <article key={asset.id} className="card">
            <div className="row">
              <strong>{asset.name}</strong>
              <span className={`pill ${asset.status.toLowerCase()}`}>{asset.status}</span>
            </div>
            <p className="muted">{asset.type}</p>
            <p className="metric">{asset.score}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
