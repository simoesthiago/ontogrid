"use client";

import {
  type AnalysisFieldsResponse,
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
  type SavedViewItem,
  createSavedView,
  deleteSavedView,
  getAnalysisFields,
  getSavedViews,
  runAnalysisQuery,
  updateSavedView,
} from "../lib/api";
import { buildDefaultViewConfig } from "../lib/view-defaults";
import { slugifyLabel, titleCaseToken } from "../lib/energy-hub";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { startTransition, useState } from "react";

interface CanvasDatasetOption {
  id: string;
  name: string;
  sourceCode?: string;
}

interface CanvasTab {
  id: string;
  name: string;
  datasetId: string;
  config: AnalysisViewConfig;
  fields: AnalysisFieldsResponse;
  result: AnalysisQueryResponse;
  savedViewId?: string;
  description?: string | null;
  isDirty: boolean;
  isLoading: boolean;
}

function buildLocalTabId(name: string) {
  return `tab-${slugifyLabel(name)}-${Math.random().toString(36).slice(2, 8)}`;
}

function createTabFromSavedView(
  savedView: SavedViewItem,
  fields: AnalysisFieldsResponse,
  result: AnalysisQueryResponse,
): CanvasTab {
  return {
    id: buildLocalTabId(savedView.name),
    name: savedView.name,
    datasetId: savedView.config_json.dataset_id,
    config: savedView.config_json,
    fields,
    result,
    savedViewId: savedView.id,
    description: savedView.description,
    isDirty: false,
    isLoading: false,
  };
}

function createDraftTab(params: {
  name: string;
  datasetId: string;
  fields: AnalysisFieldsResponse;
  config: AnalysisViewConfig;
  result: AnalysisQueryResponse;
}): CanvasTab {
  return {
    id: buildLocalTabId(params.name),
    name: params.name,
    datasetId: params.datasetId,
    fields: params.fields,
    config: params.config,
    result: params.result,
    isDirty: true,
    isLoading: false,
  };
}

function extractCompatibleSeries(result: AnalysisQueryResponse) {
  const dimensionKeys = result.columns.filter((item) => item.kind === "dimension").map((item) => item.id);
  const measureKeys = result.columns.filter((item) => item.kind === "measure").map((item) => item.id);
  const categoryKey = dimensionKeys[0];
  const measureKey = measureKeys[0];
  if (!categoryKey || !measureKey) {
    return [];
  }

  return result.rows
    .map((row) => ({
      label: String(row.values[categoryKey] ?? ""),
      value: Number(row.values[measureKey] ?? 0),
    }))
    .filter((item) => Number.isFinite(item.value));
}

function BarChart({
  result,
  orientation,
}: {
  result: AnalysisQueryResponse;
  orientation: "bar" | "column";
}) {
  const series = extractCompatibleSeries(result).slice(0, 8);
  const max = Math.max(...series.map((item) => item.value), 1);

  if (!series.length) {
    return <div className="emptyState compact">Dados insuficientes para este grafico.</div>;
  }

  return (
    <div className={`chartCard ${orientation}`}>
      {series.map((item) => (
        <div key={item.label} className="chartRow">
          <span className="chartLabel">{item.label}</span>
          <div className="chartTrack">
            <span
              className="chartFill"
              style={
                orientation === "bar"
                  ? { width: `${(item.value / max) * 100}%` }
                  : { height: `${(item.value / max) * 100}%` }
              }
            />
          </div>
          <span className="chartValue">{item.value.toLocaleString("pt-BR")}</span>
        </div>
      ))}
    </div>
  );
}

function LineChart({ result }: { result: AnalysisQueryResponse }) {
  const series = extractCompatibleSeries(result).slice(0, 10);
  const max = Math.max(...series.map((item) => item.value), 1);

  if (!series.length) {
    return <div className="emptyState compact">Dados insuficientes para este grafico.</div>;
  }

  const points = series
    .map((item, index) => {
      const x = series.length === 1 ? 50 : (index / (series.length - 1)) * 100;
      const y = 100 - (item.value / max) * 100;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="lineChartWrap">
      <svg viewBox="0 0 100 100" className="lineChart">
        <polyline points={points} fill="none" stroke="currentColor" strokeWidth="2.5" />
      </svg>
      <div className="lineLegend">
        {series.map((item) => (
          <span key={item.label} className="chartLabel">
            {item.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function PieChart({ result }: { result: AnalysisQueryResponse }) {
  const series = extractCompatibleSeries(result).slice(0, 6);
  const total = series.reduce((acc, item) => acc + item.value, 0);

  if (!series.length || total <= 0) {
    return <div className="emptyState compact">Dados insuficientes para este grafico.</div>;
  }

  let accumulated = 0;
  const colors = ["#101010", "#4c4a44", "#857e70", "#c7bca7", "#d7d2c7", "#8f6743"];

  const slices = series.map((item, index) => {
    const startAngle = (accumulated / total) * Math.PI * 2;
    accumulated += item.value;
    const endAngle = (accumulated / total) * Math.PI * 2;
    const x1 = 50 + 40 * Math.cos(startAngle - Math.PI / 2);
    const y1 = 50 + 40 * Math.sin(startAngle - Math.PI / 2);
    const x2 = 50 + 40 * Math.cos(endAngle - Math.PI / 2);
    const y2 = 50 + 40 * Math.sin(endAngle - Math.PI / 2);
    const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;
    return {
      key: item.label,
      color: colors[index % colors.length],
      d: `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`,
      value: item.value,
      label: item.label,
    };
  });

  return (
    <div className="pieWrap">
      <svg viewBox="0 0 100 100" className="pieChart">
        {slices.map((slice) => (
          <path key={slice.key} d={slice.d} fill={slice.color} />
        ))}
      </svg>
      <div className="pieLegend">
        {slices.map((slice) => (
          <div key={slice.key} className="pieLegendRow">
            <span className="pieDot" style={{ background: slice.color }} />
            <span>{slice.label}</span>
            <strong>{slice.value.toLocaleString("pt-BR")}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function ResultRenderer({ tab }: { tab: CanvasTab }) {
  if (!tab.result.columns.length || !tab.result.rows.length) {
    return <div className="emptyState">Sem linhas para essa composicao.</div>;
  }

  if (tab.config.visualization.type === "table") {
    return (
      <div className="tableWrap">
        <table className="dataTable">
          <thead>
            <tr>
              {tab.result.columns.map((column) => (
                <th key={column.id}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tab.result.rows.map((row, rowIndex) => (
              <tr key={`${tab.id}-${rowIndex}`}>
                {tab.result.columns.map((column) => (
                  <td key={column.id}>{String(row.values[column.id] ?? "")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (tab.config.visualization.type === "bar") {
    return <BarChart result={tab.result} orientation="bar" />;
  }
  if (tab.config.visualization.type === "column") {
    return <BarChart result={tab.result} orientation="column" />;
  }
  if (tab.config.visualization.type === "line") {
    return <LineChart result={tab.result} />;
  }
  if (tab.config.visualization.type === "pie") {
    return <PieChart result={tab.result} />;
  }

  return <div className="emptyState compact">Visualizacao nao suportada.</div>;
}

export function EnergyCanvas({
  scopeType,
  scopeId,
  scopeLabel,
  datasetOptions,
  initialFields,
  initialQuery,
  initialConfig,
  initialViews,
  initialTitle,
  initialViewId,
  initialSavedView,
}: {
  scopeType: "dataset" | "entity";
  scopeId: string;
  scopeLabel: string;
  datasetOptions: CanvasDatasetOption[];
  initialFields: AnalysisFieldsResponse | null;
  initialQuery: AnalysisQueryResponse | null;
  initialConfig: AnalysisViewConfig | null;
  initialViews: SavedViewItem[];
  initialTitle: string;
  initialViewId?: string;
  initialSavedView?: SavedViewItem | null;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [savedViews, setSavedViews] = useState(initialViews);
  const initialTab =
    initialFields && initialQuery && initialConfig
      ? initialSavedView
        ? createTabFromSavedView(initialSavedView, initialFields, initialQuery)
        : createDraftTab({
            name: initialTitle,
            datasetId: initialConfig.dataset_id,
            fields: initialFields,
            config: initialConfig,
            result: initialQuery,
          })
      : null;
  const [tabs, setTabs] = useState<CanvasTab[]>(
    initialTab ? [initialTab] : [],
  );
  const [activeTabId, setActiveTabId] = useState<string | null>(initialTab?.id ?? null);
  const [isBusy, setIsBusy] = useState(false);

  const activeTab = tabs.find((item) => item.id === (activeTabId ?? tabs[0]?.id)) ?? tabs[0] ?? null;

  function syncViewParam(viewId?: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (viewId) {
      next.set("view", viewId);
    } else {
      next.delete("view");
    }
    startTransition(() => {
      const query = next.toString();
      router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
    });
  }

  async function createTabForDataset(datasetId: string, viewName: string, entityId?: string | null) {
    setIsBusy(true);
    try {
      const fields = await getAnalysisFields(datasetId);
      const config = buildDefaultViewConfig(fields, datasetId, entityId ?? null);
      const result = config.measures.length
        ? await runAnalysisQuery(config)
        : {
            dataset_id: datasetId,
            columns: [],
            rows: [],
            totals: {},
            applied_filters: [],
          };
      const tab = createDraftTab({
        name: viewName,
        datasetId,
        fields,
        config,
        result,
      });
      setTabs((current) => [...current, tab]);
      setActiveTabId(tab.id);
      syncViewParam(undefined);
    } finally {
      setIsBusy(false);
    }
  }

  async function createNewView() {
    const fallbackDatasetId = activeTab?.datasetId ?? datasetOptions[0]?.id;
    if (!fallbackDatasetId) {
      return;
    }

    const fallbackLabel =
      datasetOptions.find((item) => item.id === fallbackDatasetId)?.name ?? activeTab?.name ?? "Nova view";
    await createTabForDataset(
      fallbackDatasetId,
      `Nova view - ${fallbackLabel}`,
      scopeType === "entity" ? scopeId : null,
    );
  }

  async function refreshTab(tabId: string, config: AnalysisViewConfig) {
    setTabs((current) =>
      current.map((item) =>
        item.id === tabId
          ? { ...item, config, isDirty: true, isLoading: true }
          : item,
      ),
    );
    const result = config.measures.length
      ? await runAnalysisQuery(config)
      : {
          dataset_id: config.dataset_id,
          columns: [],
          rows: [],
          totals: {},
          applied_filters: [],
        };
    setTabs((current) =>
      current.map((item) =>
        item.id === tabId
          ? { ...item, config, result, isDirty: true, isLoading: false }
          : item,
      ),
    );
  }

  async function openSavedView(view: SavedViewItem) {
    const existing = tabs.find((item) => item.savedViewId === view.id);
    if (existing) {
      setActiveTabId(existing.id);
      syncViewParam(view.id);
      return;
    }

    setIsBusy(true);
    try {
      const fields = await getAnalysisFields(view.config_json.dataset_id);
      const result = view.config_json.measures.length
        ? await runAnalysisQuery(view.config_json)
        : {
            dataset_id: view.config_json.dataset_id,
            columns: [],
            rows: [],
            totals: {},
            applied_filters: [],
          };
      const tab = createTabFromSavedView(view, fields, result);
      setTabs((current) => [...current, tab]);
      setActiveTabId(tab.id);
      syncViewParam(view.id);
    } finally {
      setIsBusy(false);
    }
  }

  async function saveCurrentTab(saveAs: boolean) {
    if (!activeTab) {
      return;
    }

    const requestedName = window.prompt(
      saveAs || !activeTab.savedViewId ? "Nome da view" : "Atualizar nome da view",
      activeTab.name,
    );
    if (!requestedName) {
      return;
    }

    setIsBusy(true);
    try {
      let savedItem: SavedViewItem;
      if (saveAs || !activeTab.savedViewId) {
        savedItem = await createSavedView({
          scope_type: scopeType,
          scope_id: scopeId,
          name: requestedName,
          description: activeTab.description,
          config_json: activeTab.config,
        });
      } else {
        savedItem = await updateSavedView(activeTab.savedViewId, {
          name: requestedName,
          description: activeTab.description,
          config_json: activeTab.config,
        });
      }

      setSavedViews((current) => {
        const without = current.filter((item) => item.id !== savedItem.id);
        return [savedItem, ...without];
      });
      setTabs((current) =>
        current.map((item) =>
          item.id === activeTab.id
            ? {
                ...item,
                name: savedItem.name,
                savedViewId: savedItem.id,
                isDirty: false,
              }
            : item,
        ),
      );
      syncViewParam(savedItem.id);
    } finally {
      setIsBusy(false);
    }
  }

  async function deleteCurrentTabView() {
    if (!activeTab?.savedViewId) {
      return;
    }
    const confirmed = window.confirm("Excluir esta view salva?");
    if (!confirmed) {
      return;
    }

    setIsBusy(true);
    try {
      await deleteSavedView(activeTab.savedViewId);
      setSavedViews((current) => current.filter((item) => item.id !== activeTab.savedViewId));
      setTabs((current) =>
        current.map((item) =>
          item.id === activeTab.id
            ? { ...item, savedViewId: undefined, isDirty: true }
            : item,
        ),
      );
      syncViewParam(undefined);
    } finally {
      setIsBusy(false);
    }
  }

  async function reloadSavedViews() {
    const response = await getSavedViews({ scope_type: scopeType, scope_id: scopeId });
    setSavedViews(response.items);
  }

  function closeTab(tabId: string) {
    const remaining = tabs.filter((item) => item.id !== tabId);
    const nextActiveId =
      (activeTab?.id ?? tabs[0]?.id) === tabId ? (remaining[0]?.id ?? null) : activeTabId;
    setTabs(remaining);
    setActiveTabId(nextActiveId);
    if ((activeTab?.id ?? tabs[0]?.id) === tabId) {
      syncViewParam(undefined);
    }
  }

  async function updateActiveTabField(field: "rows" | "columns", value: string) {
    if (!activeTab) {
      return;
    }
    const nextConfig: AnalysisViewConfig = {
      ...activeTab.config,
      [field]: value ? [value] : [],
    };
    await refreshTab(activeTab.id, nextConfig);
  }

  async function updateActiveMeasure(field: string, aggregation?: AnalysisViewConfig["measures"][number]["aggregation"]) {
    if (!activeTab) {
      return;
    }
    const currentMeasure = activeTab.config.measures[0];
    const nextField = field || currentMeasure?.field || "";
    const nextAggregation = aggregation || currentMeasure?.aggregation || "sum";
    const nextConfig: AnalysisViewConfig = {
      ...activeTab.config,
      measures: nextField ? [{ field: nextField, aggregation: nextAggregation }] : [],
    };
    await refreshTab(activeTab.id, nextConfig);
  }

  async function updateVisualization(type: AnalysisViewConfig["visualization"]["type"]) {
    if (!activeTab) {
      return;
    }
    const nextConfig: AnalysisViewConfig = {
      ...activeTab.config,
      visualization: { type },
    };
    await refreshTab(activeTab.id, nextConfig);
  }

  const activeSavedViewId = activeTab?.savedViewId ?? initialViewId;

  return (
    <section className="panel canvasPanel">
      <div className="sectionHeading">
        <div>
          <h3 className="panelTitle">{scopeLabel}</h3>
          <p className="panelText">
            Canvas com abas, views salvas por usuario e uma composicao por dataset.
          </p>
        </div>
        <div className="toolbarActions">
          <button type="button" className="iconButton" onClick={() => void createNewView()} disabled={isBusy}>
            Nova view
          </button>
          <button
            type="button"
            className="iconButton"
            onClick={() => void saveCurrentTab(false)}
            disabled={!activeTab || isBusy}
          >
            Salvar
          </button>
          <button
            type="button"
            className="iconButton"
            onClick={() => void saveCurrentTab(true)}
            disabled={!activeTab || isBusy}
          >
            Salvar como
          </button>
          <button
            type="button"
            className="iconButton"
            onClick={() => void deleteCurrentTabView()}
            disabled={!activeTab?.savedViewId || isBusy}
          >
            Excluir
          </button>
        </div>
      </div>

      <div className="canvasMetaGrid">
        <div className="savedViewsColumn">
          <div className="sectionHeading">
            <h4 className="panelTitle">Views salvas</h4>
            <button type="button" className="iconButton" onClick={() => void reloadSavedViews()}>
              Atualizar
            </button>
          </div>
          <div className="savedViewsList">
            {savedViews.length ? (
              savedViews.map((view) => (
                <button
                  type="button"
                  key={view.id}
                  className={`savedViewButton ${activeSavedViewId === view.id ? "isActive" : ""}`}
                  onClick={() => void openSavedView(view)}
                >
                  <strong>{view.name}</strong>
                  <small>{titleCaseToken(view.config_json.visualization.type)}</small>
                </button>
              ))
            ) : (
              <div className="emptyState compact">Nenhuma view salva ainda.</div>
            )}
          </div>
        </div>

        <div className="savedViewsColumn">
          <div className="sectionHeading">
            <h4 className="panelTitle">Sugestoes</h4>
            <span className="panelHint">{datasetOptions.length} datasets</span>
          </div>
          <div className="savedViewsList">
            {datasetOptions.map((dataset) => (
              <button
                type="button"
                key={dataset.id}
                className="savedViewButton"
                onClick={() =>
                  void createTabForDataset(
                    dataset.id,
                    dataset.name,
                    scopeType === "entity" ? scopeId : null,
                  )
                }
                disabled={isBusy}
              >
                <strong>{dataset.name}</strong>
                <small>{dataset.sourceCode?.toUpperCase() || "dataset"}</small>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="tabsRow">
        {tabs.map((tab) => (
          <button
            type="button"
            key={tab.id}
            className={`tabButton ${(activeTab?.id ?? tabs[0]?.id) === tab.id ? "isActive" : ""}`}
            onClick={() => {
              setActiveTabId(tab.id);
              syncViewParam(tab.savedViewId);
            }}
          >
            <span>{tab.name}</span>
            <small>{tab.isDirty ? "draft" : "saved"}</small>
          </button>
        ))}
      </div>

      {activeTab ? (
        <div className="canvasBody">
          <div className="builderToolbar">
            <label className="builderField">
              <span>Dataset</span>
              <select value={activeTab.datasetId} disabled>
                <option value={activeTab.datasetId}>{activeTab.datasetId}</option>
              </select>
            </label>

            <label className="builderField">
              <span>Linhas</span>
              <select
                value={activeTab.config.rows[0] ?? ""}
                onChange={(event) => void updateActiveTabField("rows", event.target.value)}
              >
                <option value="">Nenhuma</option>
                {activeTab.fields.dimensions.map((field) => (
                  <option key={field.id} value={field.id}>
                    {field.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="builderField">
              <span>Colunas</span>
              <select
                value={activeTab.config.columns[0] ?? ""}
                onChange={(event) => void updateActiveTabField("columns", event.target.value)}
              >
                <option value="">Nenhuma</option>
                {activeTab.fields.dimensions.map((field) => (
                  <option key={field.id} value={field.id}>
                    {field.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="builderField">
              <span>Metrica</span>
              <select
                value={activeTab.config.measures[0]?.field ?? ""}
                onChange={(event) => void updateActiveMeasure(event.target.value)}
              >
                {activeTab.fields.metrics.map((metric) => (
                  <option key={metric.field} value={metric.field}>
                    {metric.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="builderField">
              <span>Agregacao</span>
              <select
                value={activeTab.config.measures[0]?.aggregation ?? "sum"}
                onChange={(event) =>
                  void updateActiveMeasure(
                    activeTab.config.measures[0]?.field ?? activeTab.fields.default_measure ?? "",
                    event.target.value as AnalysisViewConfig["measures"][number]["aggregation"],
                  )
                }
              >
                {["sum", "avg", "count", "min", "max"].map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="builderField">
              <span>Visualizacao</span>
              <select
                value={activeTab.config.visualization.type}
                onChange={(event) =>
                  void updateVisualization(event.target.value as AnalysisViewConfig["visualization"]["type"])
                }
              >
                {["table", "bar", "column", "line", "pie"].map((item) => (
                  <option key={item} value={item}>
                    {titleCaseToken(item)}
                  </option>
                ))}
              </select>
            </label>

            <button type="button" className="iconButton" onClick={() => closeTab(activeTab.id)}>
              Fechar aba
            </button>
          </div>

          {scopeType === "entity" && activeTab.config.entity_id ? (
            <div className="entityFilterBanner">
              Entidade travada nesta view: <strong>{activeTab.config.entity_id}</strong>
            </div>
          ) : null}

          {activeTab.isLoading ? (
            <div className="emptyState">Atualizando view...</div>
          ) : (
            <ResultRenderer tab={activeTab} />
          )}
        </div>
      ) : (
        <div className="emptyState">
          Nenhuma aba aberta. Selecione uma sugestao para iniciar o canvas.
        </div>
      )}
    </section>
  );
}
