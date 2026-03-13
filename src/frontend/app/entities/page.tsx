import Link from "next/link";

import {
  type AnalysisFieldsResponse,
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
  type EntityProfileResponse,
  type SavedViewItem,
  getAnalysisFields,
  getDataset,
  getEntities,
  getEntityProfile,
  getSavedViews,
  runAnalysisQuery,
} from "../../lib/api";
import { EnergyCanvas } from "../../components/energy-canvas";
import {
  ENERGY_HUB_ENTITY_TYPES,
  getQueryValue,
  titleCaseToken,
} from "../../lib/energy-hub";
import { buildDefaultViewConfig, resolveInitialView } from "../../lib/view-defaults";

export const dynamic = "force-dynamic";

function buildHref(
  current: URLSearchParams,
  updates: Record<string, string | undefined>,
) {
  const next = new URLSearchParams(current);

  for (const [key, value] of Object.entries(updates)) {
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
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
  const requestedViewId = getQueryValue(resolvedSearchParams.view);
  const searchState = new URLSearchParams();

  if (query) {
    searchState.set("q", query);
  }
  if (selectedType) {
    searchState.set("type", selectedType);
  }

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
  let datasetOptions: Array<{ id: string; name: string; sourceCode?: string }> = [];
  let initialFields: AnalysisFieldsResponse | null = null;
  let initialQuery: AnalysisQueryResponse | null = null;
  let initialConfig: AnalysisViewConfig | null = null;
  let initialViews: SavedViewItem[] = [];
  let initialTitle = "Nova view";
  let initialSavedView: SavedViewItem | null = null;

  if (selectedEntity) {
    profile = await getEntityProfile(selectedEntity.id);
    const recentDatasetIds = Array.from(
      new Map(profile.recent_versions.map((item) => [item.dataset_id, item])).values(),
    );

    const datasetEntries = await Promise.all(
      recentDatasetIds.map(async (item) => {
        const dataset = await getDataset(item.dataset_id);
        return {
          id: item.dataset_id,
          name: dataset.name,
          sourceCode: dataset.source_code,
        };
      }),
    );
    datasetOptions = datasetEntries;

    if (datasetOptions[0]) {
      [initialFields, initialViews] = await Promise.all([
        getAnalysisFields(datasetOptions[0].id),
        getSavedViews({ scope_type: "entity", scope_id: selectedEntity.id }).then((response) => response.items),
      ]);
      initialSavedView = resolveInitialView(initialViews, requestedViewId);
      initialConfig =
        initialSavedView?.config_json ??
        buildDefaultViewConfig(initialFields, datasetOptions[0].id, selectedEntity.id);
      initialQuery = initialConfig.measures.length
        ? await runAnalysisQuery(initialConfig)
        : {
            dataset_id: datasetOptions[0].id,
            columns: [],
            rows: [],
            totals: {},
            applied_filters: [],
          };
      initialTitle = initialSavedView?.name ?? `${profile.identity.name} / ${datasetOptions[0].name}`;
    }
  }

  return (
    <section className="stack pageStack">
      <header className="pageHeader">
        <p className="pageKicker">Energy Hub</p>
        <h1 className="pageTitle">Entidades</h1>
        <p className="pageSubtitle">
          O usuario escolhe a entidade e abre views no canvas conforme os datasets disponiveis
          para aquela instancia.
        </p>
      </header>

      <div className="workspaceLayout entitiesLayout">
        <aside className="panel listPane">
          <form action="/entities" className="searchForm">
            <input
              className="searchInput"
              type="search"
              name="q"
              defaultValue={query}
              placeholder="Buscar entidade"
              aria-label="Buscar entidade"
            />
            <input type="hidden" name="type" value={activeGroup.id} />
          </form>

          <div className="panelSection">
            <div className="sectionHeading">
              <h2 className="panelTitle">Entidades</h2>
              <span className="panelCount">{entityCatalog.total}</span>
            </div>

            <div className="entityTypeStack">
              {entitiesByType.map((group) => (
                <div key={group.id} className="entityTypeCard">
                  <div className="sectionHeading">
                    <Link
                      href={buildHref(searchState, { type: group.id, entity: undefined, view: undefined })}
                      className={`entityTypeLink ${activeGroup.id === group.id ? "isActive" : ""}`}
                    >
                      {group.label}
                    </Link>
                    <span className="panelCount">{group.items.length}</span>
                  </div>
                  <p className="panelText">{group.description}</p>

                  {activeGroup.id === group.id ? (
                    <div className="entityItemStack">
                      {group.items.length ? (
                        group.items.slice(0, 14).map((item) => (
                          <Link
                            key={item.id}
                            href={buildHref(searchState, { type: group.id, entity: item.id, view: undefined })}
                            className={`entityItem ${selectedEntity?.id === item.id ? "isActive" : ""}`}
                          >
                            <span>{item.name}</span>
                            <small>{item.canonical_code || item.jurisdiction}</small>
                          </Link>
                        ))
                      ) : (
                        <div className="emptyState compact">
                          Nenhuma entidade desse tipo foi materializada ainda.
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        </aside>

        <div className="stack">
          {selectedEntity && profile && initialFields && initialQuery && initialConfig ? (
            <>
              <section className="panel heroPanel">
                <div className="heroHeading">
                  <div>
                    <p className="pageKicker">{titleCaseToken(profile.identity.entity_type)}</p>
                    <h2 className="workspaceTitle">{profile.identity.name}</h2>
                    <p className="pageSubtitle">
                      {profile.identity.canonical_code || "Sem codigo canonico"} /{" "}
                      {profile.identity.jurisdiction}
                    </p>
                  </div>
                  <div className="statusStack">
                    <span className="statusPill">{profile.graph_status}</span>
                    <span className="statusPill mutedPill">{profile.recent_versions.length} datasets</span>
                  </div>
                </div>
              </section>

              <EnergyCanvas
                scopeType="entity"
                scopeId={selectedEntity.id}
                scopeLabel={profile.identity.name}
                datasetOptions={datasetOptions}
                initialFields={initialFields}
                initialQuery={initialQuery}
                initialConfig={initialConfig}
                initialViews={initialViews}
                initialTitle={initialTitle}
                initialViewId={requestedViewId}
                initialSavedView={initialSavedView}
              />
            </>
          ) : (
            <section className="panel emptyState">
              Selecione uma entidade materializada para abrir o canvas.
            </section>
          )}
        </div>
      </div>
    </section>
  );
}
