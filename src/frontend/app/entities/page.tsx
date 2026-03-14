import Link from "next/link";

import {
  type AnalysisFieldsResponse,
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
  type EntityProfileResponse,
  getAnalysisFields,
  getDataset,
  getEntities,
  getEntityProfile,
  runAnalysisQuery,
} from "../../lib/api";
import { EnergyCanvas } from "../../components/energy-canvas";
import { ENERGY_HUB_ENTITY_TYPES, getQueryValue, titleCaseToken } from "../../lib/energy-hub";
import { buildDefaultViewConfig } from "../../lib/view-defaults";

export const dynamic = "force-dynamic";

function buildHref(current: URLSearchParams, updates: Record<string, string | undefined>) {
  const next = new URLSearchParams(current);
  for (const [key, value] of Object.entries(updates)) {
    if (value) next.set(key, value); else next.delete(key);
  }
  const query = next.toString();
  return query ? `/entities?${query}` : "/entities";
}

export default async function EntitiesPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolvedSearchParams = await searchParams;
  const query = getQueryValue(resolvedSearchParams.q)?.trim() ?? "";
  const selectedType = getQueryValue(resolvedSearchParams.type) ?? "agent";
  const requestedEntityId = getQueryValue(resolvedSearchParams.entity);
  const searchState = new URLSearchParams();

  if (query) searchState.set("q", query);
  if (selectedType) searchState.set("type", selectedType);

  const entityCatalog = await getEntities({ q: query || undefined, limit: 400 });
  const entitiesByType = ENERGY_HUB_ENTITY_TYPES.map((group) => ({
    ...group,
    items: entityCatalog.items.filter((item) => item.entity_type === group.id),
  }));

  const activeGroup =
    entitiesByType.find((group) => group.id === selectedType) ??
    entitiesByType.find((group) => group.items.length > 0) ??
    entitiesByType[0];

  const selectedEntity =
    activeGroup.items.find((item) => item.id === requestedEntityId) ??
    activeGroup.items[0] ??
    null;

  let profile: EntityProfileResponse | null = null;
  let initialFields: AnalysisFieldsResponse | null = null;
  let initialQuery: AnalysisQueryResponse | null = null;
  let initialConfig: AnalysisViewConfig | null = null;
  let firstDatasetName = "";

  if (selectedEntity) {
    profile = await getEntityProfile(selectedEntity.id);
    const recentDatasetIds = Array.from(
      new Map(profile.recent_versions.map((item) => [item.dataset_id, item])).values(),
    );

    if (recentDatasetIds[0]) {
      const firstDatasetId = recentDatasetIds[0].dataset_id;
      const [dataset, fields] = await Promise.all([
        getDataset(firstDatasetId),
        getAnalysisFields(firstDatasetId),
      ]);
      firstDatasetName = dataset.name;
      initialFields = fields;
      initialConfig = buildDefaultViewConfig(initialFields, firstDatasetId, selectedEntity.id);
      initialQuery = initialConfig.measures.length
        ? await runAnalysisQuery(initialConfig)
        : { dataset_id: firstDatasetId, columns: [], rows: [], totals: {}, applied_filters: [] };
    }
  }

  return (
    <div className="pageWorkspace">
      <div className="pageTitleBar">
        <h1 className="pageTitle">Entidades</h1>
      </div>

      <div className="workspaceLayout entitiesLayout stretchLayout">
        <aside className="panel listPane">
          <div className="sectionHeading">
            <h2 className="panelTitle">Entidades</h2>
            <span className="panelCount">{entityCatalog.total}</span>
          </div>

          <form action="/entities" className="searchForm">
            <input
              className="searchInput"
              type="search"
              name="q"
              defaultValue={query}
              placeholder="Buscar entidade"
              aria-label="Buscar entidade"
            />
          </form>

          <div className="panelSection">
            {entitiesByType.some((g) => g.items.length > 0) ? (
              <div className="treeGroups">
                {entitiesByType.map((group) => (
                  <details key={group.id} className="treeGroup" open={activeGroup.id === group.id}>
                    <summary className="treeGroupHeader">
                      <svg className="treeGroupIcon" width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path className="folderClosed" d="M1.5 4.5h4l1.5 2h7.5v7H1.5z" />
                        <path className="folderOpen" d="M1.5 4.5h4l1.5 2h7.5v2M1.5 8h13v5.5H1.5z" />
                      </svg>
                      <span className="treeGroupLabel">{group.label}</span>
                      <span className="panelCount">{group.items.length}</span>
                    </summary>
                    <div className="treeItems">
                      {group.items.length ? (
                        group.items.slice(0, 14).map((item) => (
                          <Link
                            key={item.id}
                            href={buildHref(searchState, { type: group.id, entity: item.id })}
                            className={`treeItem ${selectedEntity?.id === item.id ? "isActive" : ""}`}
                          >
                            <span>{item.name}</span>
                          </Link>
                        ))
                      ) : (
                        <div className="emptyState compact">Nenhuma entidade desse tipo materializada.</div>
                      )}
                    </div>
                  </details>
                ))}
              </div>
            ) : (
              <div className="emptyState">Nenhuma entidade bateu com o filtro atual.</div>
            )}
          </div>
        </aside>

        <div className="stack">
          {selectedEntity && profile ? (
            <>
              <section className="panel heroPanel">
                <div className="heroHeading">
                  <div>
                    <p className="pageKicker">{titleCaseToken(profile.identity.entity_type)}</p>
                    <h2 className="workspaceTitle">{profile.identity.name}</h2>
                    <p className="pageSubtitle">
                      {profile.identity.canonical_code || "Sem código canônico"} /{" "}
                      {profile.identity.jurisdiction}
                    </p>
                  </div>
                  <div className="statusStack">
                    <span className="statusPill">{profile.graph_status}</span>
                    <span className="statusPill mutedPill">{profile.recent_versions.length} datasets</span>
                  </div>
                </div>
              </section>

              {initialFields && initialQuery && initialConfig ? (
                <EnergyCanvas
                  scopeLabel={firstDatasetName}
                  initialFields={initialFields}
                  initialQuery={initialQuery}
                  initialConfig={initialConfig}
                  initialTitle={`${profile.identity.name} — ${firstDatasetName}`}
                  entityId={selectedEntity.id}
                />
              ) : (
                <section className="panel emptyState">
                  Nenhum dataset associado a esta entidade.
                </section>
              )}
            </>
          ) : (
            <section className="panel emptyState">
              Selecione uma entidade para visualizar os dados.
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
