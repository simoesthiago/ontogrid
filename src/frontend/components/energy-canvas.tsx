"use client";

import {
  type AnalysisFieldsResponse,
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
} from "../lib/api";
import { slugifyLabel } from "../lib/energy-hub";

interface CanvasTab {
  id: string;
  name: string;
  config: AnalysisViewConfig;
  result: AnalysisQueryResponse;
}

function buildTabId(name: string) {
  return `tab-${slugifyLabel(name)}-${Math.random().toString(36).slice(2, 8)}`;
}

function extractCompatibleSeries(result: AnalysisQueryResponse) {
  const dimensionKeys = result.columns.filter((c) => c.kind === "dimension").map((c) => c.id);
  const measureKeys = result.columns.filter((c) => c.kind === "measure").map((c) => c.id);
  const categoryKey = dimensionKeys[0];
  const measureKey = measureKeys[0];
  if (!categoryKey || !measureKey) return [];
  return result.rows
    .map((row) => ({
      label: String(row.values[categoryKey] ?? ""),
      value: Number(row.values[measureKey] ?? 0),
    }))
    .filter((item) => Number.isFinite(item.value));
}

function BarChart({ result, orientation }: { result: AnalysisQueryResponse; orientation: "bar" | "column" }) {
  const series = extractCompatibleSeries(result).slice(0, 8);
  const max = Math.max(...series.map((s) => s.value), 1);
  if (!series.length) return <div className="emptyState compact">Dados insuficientes para este gráfico.</div>;
  return (
    <div className={`chartCard ${orientation}`}>
      {series.map((item) => (
        <div key={item.label} className="chartRow">
          <span className="chartLabel">{item.label}</span>
          <div className="chartTrack">
            <span
              className="chartFill"
              style={orientation === "bar" ? { width: `${(item.value / max) * 100}%` } : { height: `${(item.value / max) * 100}%` }}
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
  const max = Math.max(...series.map((s) => s.value), 1);
  if (!series.length) return <div className="emptyState compact">Dados insuficientes para este gráfico.</div>;
  const points = series
    .map((item, i) => {
      const x = series.length === 1 ? 50 : (i / (series.length - 1)) * 100;
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
        {series.map((item) => <span key={item.label} className="chartLabel">{item.label}</span>)}
      </div>
    </div>
  );
}

function PieChart({ result }: { result: AnalysisQueryResponse }) {
  const series = extractCompatibleSeries(result).slice(0, 6);
  const total = series.reduce((acc, s) => acc + s.value, 0);
  if (!series.length || total <= 0) return <div className="emptyState compact">Dados insuficientes para este gráfico.</div>;
  let accumulated = 0;
  const colors = ["#4169e1", "#2dc87a", "#e07b3d", "#9b6fe8", "#36b8d8", "#e05252"];
  const slices = series.map((item, i) => {
    const startAngle = (accumulated / total) * Math.PI * 2;
    accumulated += item.value;
    const endAngle = (accumulated / total) * Math.PI * 2;
    const x1 = 50 + 40 * Math.cos(startAngle - Math.PI / 2);
    const y1 = 50 + 40 * Math.sin(startAngle - Math.PI / 2);
    const x2 = 50 + 40 * Math.cos(endAngle - Math.PI / 2);
    const y2 = 50 + 40 * Math.sin(endAngle - Math.PI / 2);
    return {
      key: item.label, color: colors[i % colors.length], value: item.value, label: item.label,
      d: `M 50 50 L ${x1} ${y1} A 40 40 0 ${endAngle - startAngle > Math.PI ? 1 : 0} 1 ${x2} ${y2} Z`,
    };
  });
  return (
    <div className="pieWrap">
      <svg viewBox="0 0 100 100" className="pieChart">
        {slices.map((s) => <path key={s.key} d={s.d} fill={s.color} />)}
      </svg>
      <div className="pieLegend">
        {slices.map((s) => (
          <div key={s.key} className="pieLegendRow">
            <span className="pieDot" style={{ background: s.color }} />
            <span>{s.label}</span>
            <strong>{s.value.toLocaleString("pt-BR")}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function TableView({ tab }: { tab: CanvasTab }) {
  return (
    <div className="tableWrap">
      <table className="dataTable">
        <thead>
          <tr>{tab.result.columns.map((col) => <th key={col.id}>{col.label}</th>)}</tr>
        </thead>
        <tbody>
          {tab.result.rows.map((row, i) => (
            <tr key={`${tab.id}-${i}`}>
              {tab.result.columns.map((col) => <td key={col.id}>{String(row.values[col.id] ?? "")}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ResultRenderer({ tab }: { tab: CanvasTab }) {
  if (!tab.result.columns.length || !tab.result.rows.length) {
    return <div className="emptyState">Sem dados para essa composição.</div>;
  }
  const type = tab.config.visualization.type;
  if (type === "table") return <TableView tab={tab} />;
  if (type === "bar") return <BarChart result={tab.result} orientation="bar" />;
  if (type === "column") return <BarChart result={tab.result} orientation="column" />;
  if (type === "line") return <LineChart result={tab.result} />;
  if (type === "pie") return <PieChart result={tab.result} />;
  return <div className="emptyState compact">Visualização não suportada.</div>;
}

function vizTypeLabel(type: string) {
  if (type === "table") return "Tabela";
  return "Gráfico";
}

function VizIcon({ type }: { type: string }) {
  if (type === "table") {
    return (
      <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <rect x="1.5" y="1.5" width="13" height="13" rx="1" />
        <line x1="1.5" y1="5.5" x2="14.5" y2="5.5" />
        <line x1="1.5" y1="9.5" x2="14.5" y2="9.5" />
        <line x1="6" y1="5.5" x2="6" y2="14.5" />
      </svg>
    );
  }
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="1" y="8" width="3" height="7" fill="currentColor" />
      <rect x="6" y="5" width="3" height="10" fill="currentColor" />
      <rect x="11" y="2" width="3" height="13" fill="currentColor" />
    </svg>
  );
}

export function EnergyCanvas({
  scopeLabel,
  initialFields: _initialFields,
  initialQuery,
  initialConfig,
  initialTitle,
  entityId,
}: {
  scopeLabel: string;
  initialFields: AnalysisFieldsResponse;
  initialQuery: AnalysisQueryResponse;
  initialConfig: AnalysisViewConfig;
  initialTitle: string;
  entityId?: string | null;
}) {
  const initialTab: CanvasTab = {
    id: buildTabId(initialTitle),
    name: initialTitle,
    config: initialConfig,
    result: initialQuery,
    isLoading: false,
  };

  return (
    <section className="panel canvasPanel">
      <div className="canvasHeader">
        <h3 className="canvasTitle">{scopeLabel}</h3>
        <VizIcon type={initialTab.config.visualization.type} />
      </div>

      <div className="canvasBody">
        {entityId ? (
          <div className="entityFilterBanner">
            Filtrado por entidade: <strong>{entityId}</strong>
          </div>
        ) : null}
        <ResultRenderer tab={initialTab} />
      </div>
    </section>
  );
}
