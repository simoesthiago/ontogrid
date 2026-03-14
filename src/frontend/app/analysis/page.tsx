import Link from "next/link";

import {
  type AnalysisFieldsResponse,
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
  type DatasetDetailResponse,
  getAnalysisFields,
  getDataset,
  getDatasets,
  runAnalysisQuery,
} from "../../lib/api";
import { EnergyCanvas } from "../../components/energy-canvas";
import { SearchForm } from "./search-form";
import { getQueryValue, titleCaseToken } from "../../lib/energy-hub";
import { buildDefaultViewConfig } from "../../lib/view-defaults";

export const dynamic = "force-dynamic";

function buildHref(current: URLSearchParams, updates: Record<string, string | undefined>) {
  const next = new URLSearchParams(current);
  for (const [key, value] of Object.entries(updates)) {
    if (value) next.set(key, value); else next.delete(key);
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
  const searchState = new URLSearchParams();

  if (query) searchState.set("q", query);
  if (sourceFilter && sourceFilter !== "all") searchState.set("source", sourceFilter);

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
  let selectedDataset: DatasetDetailResponse | null = null;

  if (selectedDatasetListItem) {
    selectedDataset = await getDataset(selectedDatasetListItem.id);
    initialFields = await getAnalysisFields(selectedDatasetListItem.id);
    initialConfig = buildDefaultViewConfig(initialFields, selectedDatasetListItem.id);
    initialQuery = initialConfig.measures.length
      ? await runAnalysisQuery(initialConfig)
      : { dataset_id: selectedDatasetListItem.id, columns: [], rows: [], totals: {}, applied_filters: [] };
  }

  const groupedDatasets = datasetsResponse.items.reduce<Map<string, Map<string, typeof datasetsResponse.items>>>(
    (acc, item) => {
      const bySource = acc.get(item.source_code) ?? new Map<string, typeof datasetsResponse.items>();
      const byDomain = bySource.get(item.domain) ?? [];
      byDomain.push(item);
      bySource.set(item.domain, byDomain);
      acc.set(item.source_code, bySource);
      return acc;
    },
    new Map(),
  );

  return (
    <div className="pageWorkspace">
      <div className="pageTitleBar">
        <h1 className="pageTitle">Analytics</h1>
      </div>

      <div className="workspaceLayout stretchLayout">
        <aside className="panel listPane">
          <div className="sectionHeading">
            <h2 className="panelTitle">Datasets</h2>
            <span className="panelCount">{datasetsResponse.total}</span>
          </div>

          <SearchForm query={query} sourceFilter={sourceFilter} />

          <div className="panelSection">
            {groupedDatasets.size ? (
              Array.from(groupedDatasets.entries()).map(([source, domains]) => (
                <div key={source} className="treeSection">
                  <p className="treeTitle">{source.toUpperCase()}</p>
                  <div className="treeGroups">
                    {Array.from(domains.entries()).map(([domain, items]) => (
                      <details key={domain} className="treeGroup">
                        <summary className="treeGroupHeader">
                          <svg className="treeGroupIcon" width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <path className="folderClosed" d="M1.5 4.5h4l1.5 2h7.5v7H1.5z" />
                            <path className="folderOpen" d="M1.5 4.5h4l1.5 2h7.5v2M1.5 8h13v5.5H1.5z" />
                          </svg>
                          <span className="treeGroupLabel">{titleCaseToken(domain)}</span>
                          <span className="panelCount">{items.length}</span>
                        </summary>
                        <div className="treeItems">
                          {items.slice(0, 12).map((item) => (
                            <Link
                              key={item.id}
                              href={buildHref(searchState, { dataset: item.id })}
                              className={`treeItem ${selectedDatasetListItem?.id === item.id ? "isActive" : ""}`}
                            >
                              <span>{item.name}</span>
                            </Link>
                          ))}
                        </div>
                      </details>
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
              scopeLabel={selectedDataset.name}
              initialFields={initialFields}
              initialQuery={initialQuery}
              initialConfig={initialConfig}
              initialTitle={selectedDataset.name}
            />
          ) : (
            <section className="panel emptyState">
              Selecione um dataset para visualizar os dados.
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
