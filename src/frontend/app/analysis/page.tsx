import Link from "next/link";

import {
  type AnalysisFieldsResponse,
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
  type DatasetDetailResponse,
  type SavedViewItem,
  getAnalysisFields,
  getDataset,
  getDatasets,
  getSavedViews,
  runAnalysisQuery,
} from "../../lib/api";
import { EnergyCanvas } from "../../components/energy-canvas";
import {
  ENERGY_HUB_SOURCES,
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
  return query ? `/analysis?${query}` : "/analysis";
}

export default async function AnalysisPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolvedSearchParams = await searchParams;
  const query = getQueryValue(resolvedSearchParams.q)?.trim() ?? "";
  const sourceFilter = getQueryValue(resolvedSearchParams.source) ?? "all";
  const requestedDatasetId = getQueryValue(resolvedSearchParams.dataset);
  const requestedViewId = getQueryValue(resolvedSearchParams.view);
  const searchState = new URLSearchParams();

  if (query) {
    searchState.set("q", query);
  }
  if (sourceFilter && sourceFilter !== "all") {
    searchState.set("source", sourceFilter);
  }

  const datasetsResponse = await getDatasets({
    limit: 400,
    q: query || undefined,
    source: sourceFilter !== "all" ? sourceFilter : undefined,
  });

  const selectedDatasetListItem =
    datasetsResponse.items.find((item) => item.id === requestedDatasetId) ??
    datasetsResponse.items[0] ??
    null;

  let initialFields: AnalysisFieldsResponse | null = null;
  let initialQuery: AnalysisQueryResponse | null = null;
  let initialConfig: AnalysisViewConfig | null = null;
  let initialViews: SavedViewItem[] = [];
  let initialTitle = "Nova view";
  let initialSavedView: SavedViewItem | null = null;
  let selectedDataset: DatasetDetailResponse | null = null;

  if (selectedDatasetListItem) {
    selectedDataset = await getDataset(selectedDatasetListItem.id);
    [initialFields, initialViews] = await Promise.all([
      getAnalysisFields(selectedDatasetListItem.id),
      getSavedViews({ scope_type: "dataset", scope_id: selectedDatasetListItem.id }).then((response) => response.items),
    ]);
    initialSavedView = resolveInitialView(initialViews, requestedViewId);
    initialConfig = initialSavedView?.config_json ?? buildDefaultViewConfig(initialFields, selectedDatasetListItem.id);
    initialQuery = initialConfig.measures.length
      ? await runAnalysisQuery(initialConfig)
      : {
          dataset_id: selectedDatasetListItem.id,
          columns: [],
          rows: [],
          totals: {},
          applied_filters: [],
        };
    initialTitle = initialSavedView?.name ?? selectedDataset.name;
  }

  const groupedDatasets = datasetsResponse.items.reduce<
    Map<string, Map<string, typeof datasetsResponse.items>>
  >((acc, item) => {
    const bySource = acc.get(item.source_code) ?? new Map<string, typeof datasetsResponse.items>();
    const byDomain = bySource.get(item.domain) ?? [];
    byDomain.push(item);
    bySource.set(item.domain, byDomain);
    acc.set(item.source_code, bySource);
    return acc;
  }, new Map());

  return (
    <section className="stack pageStack">
      <header className="pageHeader">
        <p className="pageKicker">Energy Hub</p>
        <h1 className="pageTitle">Analysis</h1>
        <p className="pageSubtitle">
          O usuario abre datasets por grupos e trabalha no canvas com abas, views salvas e
          visualizacoes dinamicas.
        </p>
      </header>

      <div className="workspaceLayout">
        <aside className="panel listPane">
          <form action="/analysis" className="searchForm">
            <input type="hidden" name="source" value={sourceFilter} />
            <input
              className="searchInput"
              type="search"
              name="q"
              defaultValue={query}
              placeholder="Buscar dataset"
              aria-label="Buscar dataset"
            />
          </form>

          <div className="filterChips">
            {ENERGY_HUB_SOURCES.map((source) => (
              <Link
                key={source.id}
                href={buildHref(searchState, {
                  source: source.id === "all" ? undefined : source.id,
                  dataset: undefined,
                  view: undefined,
                })}
                className={`filterChip ${sourceFilter === source.id ? "isSelected" : ""}`}
              >
                {source.label}
              </Link>
            ))}
          </div>

          <div className="panelSection">
            <div className="sectionHeading">
              <h2 className="panelTitle">Datasets</h2>
              <span className="panelCount">{datasetsResponse.total}</span>
            </div>

            {groupedDatasets.size ? (
              Array.from(groupedDatasets.entries()).map(([source, domains]) => (
                <div key={source} className="treeSection">
                  <p className="treeTitle">{source.toUpperCase()}</p>
                  <div className="treeGroups">
                    {Array.from(domains.entries()).map(([domain, items]) => (
                      <div key={domain} className="treeGroup">
                        <div className="treeGroupHeader">
                          <span>{titleCaseToken(domain)}</span>
                          <span className="panelCount">{items.length}</span>
                        </div>
                        <div className="treeItems">
                          {items.slice(0, 12).map((item) => (
                            <Link
                              key={item.id}
                              href={buildHref(searchState, { dataset: item.id, view: undefined })}
                              className={`treeItem ${
                                selectedDatasetListItem?.id === item.id ? "isActive" : ""
                              }`}
                            >
                              <span>{item.name}</span>
                              <small>{item.latest_version || "sem versao"}</small>
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="emptyState">Nenhum dataset bateu com o filtro atual.</div>
            )}
          </div>
        </aside>

        <div className="stack">
          {selectedDatasetListItem && initialFields && initialQuery && initialConfig && selectedDataset ? (
            <EnergyCanvas
              scopeType="dataset"
              scopeId={selectedDatasetListItem.id}
              scopeLabel={selectedDataset.name}
              datasetOptions={[
                {
                  id: selectedDatasetListItem.id,
                  name: selectedDataset.name,
                  sourceCode: selectedDataset.source_code,
                },
              ]}
              initialFields={initialFields}
              initialQuery={initialQuery}
              initialConfig={initialConfig}
              initialViews={initialViews}
              initialTitle={initialTitle}
              initialViewId={requestedViewId}
              initialSavedView={initialSavedView}
            />
          ) : (
            <section className="panel emptyState">
              Selecione um dataset para abrir o canvas de analise.
            </section>
          )}
        </div>
      </div>
    </section>
  );
}
