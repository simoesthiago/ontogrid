export default function SettingsPage() {
  return (
    <section className="stack pageStack">
      <header className="pageHeader">
        <p className="pageKicker">Workspace</p>
        <h1 className="pageTitle">Configuracoes</h1>
        <p className="pageSubtitle">
          Esta area fica fora do fluxo principal do Energy Hub. Ela existe para ajustes do
          workspace, nao para competir com Analysis, Entidades ou Datasets.
        </p>
      </header>

      <section className="panel emptyState">
        Primeiro corte reservado para preferencias do usuario, historico e futuras opcoes do
        workspace.
      </section>
    </section>
  );
}
