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
import { buildPageHref, createSearchParams } from "../../lib/search-state";
import { buildDefaultViewConfig } from "../../lib/view-defaults";

export const dynamic = "force-dynamic";

export default async function AnalysisPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolvedSearchParams = await searchParams;
  const query = getQueryValue(resolvedSearchParams.q)?.trim() ?? "";
  const sourceFilter = getQueryValue(resolvedSearchParams.source) ?? "all";
  const requestedDatasetId = getQueryValue(resolvedSearchParams.dataset);
  const searchState = createSearchParams({
    q: query || undefined,
    source: sourceFilter !== "all" ? sourceFilter : undefined,
  });

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
                            href={buildPageHref("/analysis", searchState, { dataset: item.id })}
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
            <>
              <section className="panel heroPanel">
                <div className="heroHeading">
                  <div>
                    <p className="pageKicker">
                      {selectedDataset.source_code.toUpperCase()} / {titleCaseToken(selectedDataset.domain)}
                    </p>
                    <h2 className="workspaceTitle">{selectedDataset.name}</h2>
                    <p className="pageSubtitle">
                      {selectedDataset.description || "Sem descrição publicada para este dataset."}
                    </p>
                  </div>
                  <div className="toolbarActions">
                    <span
                      className={`statusPill ${
                        selectedDataset.ingestion_status === "published" ? "" : "mutedPill"
                      }`}
                    >
                      {selectedDataset.ingestion_status}
                    </span>
                    <Link href={`/datasets/${selectedDataset.id}`} className="inlineAction">
                      Abrir detalhe do dataset
                    </Link>
                    <Link href={`/copilot?dataset=${selectedDataset.id}`} className="inlineAction">
                      Perguntar no Copilot
                    </Link>
                  </div>
                </div>
              </section>

              <EnergyCanvas
                scopeLabel={selectedDataset.name}
                initialQuery={initialQuery}
                initialConfig={initialConfig}
              />
            </>
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
