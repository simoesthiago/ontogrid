"use client";

import {
  type AnalysisQueryResponse,
  type AnalysisViewConfig,
} from "../lib/api";

function extractCompatibleSeries(result: AnalysisQueryResponse) {
  const dimensionKeys = result.columns.filter((column) => column.kind === "dimension").map((column) => column.id);
  const measureKeys = result.columns.filter((column) => column.kind === "measure").map((column) => column.id);
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
    return <div className="emptyState compact">Dados insuficientes para este gráfico.</div>;
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
    return <div className="emptyState compact">Dados insuficientes para este gráfico.</div>;
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
  const total = series.reduce((accumulator, item) => accumulator + item.value, 0);

  if (!series.length || total <= 0) {
    return <div className="emptyState compact">Dados insuficientes para este gráfico.</div>;
  }

  const colors = ["#4169e1", "#2dc87a", "#e07b3d", "#9b6fe8", "#36b8d8", "#e05252"];
  const cumulativeTotals = series.map((_, index) =>
    series.slice(0, index + 1).reduce((accumulator, item) => accumulator + item.value, 0),
  );
  const slices = series.map((item, index) => {
    const previousTotal = index === 0 ? 0 : cumulativeTotals[index - 1];
    const currentTotal = cumulativeTotals[index];
    const startAngle = (previousTotal / total) * Math.PI * 2;
    const endAngle = (currentTotal / total) * Math.PI * 2;
    const x1 = 50 + 40 * Math.cos(startAngle - Math.PI / 2);
    const y1 = 50 + 40 * Math.sin(startAngle - Math.PI / 2);
    const x2 = 50 + 40 * Math.cos(endAngle - Math.PI / 2);
    const y2 = 50 + 40 * Math.sin(endAngle - Math.PI / 2);

    return {
      key: item.label,
      color: colors[index % colors.length],
      value: item.value,
      label: item.label,
      d: `M 50 50 L ${x1} ${y1} A 40 40 0 ${endAngle - startAngle > Math.PI ? 1 : 0} 1 ${x2} ${y2} Z`,
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

function TableView({ result }: { result: AnalysisQueryResponse }) {
  return (
    <div className="tableWrap">
      <table className="dataTable">
        <thead>
          <tr>
            {result.columns.map((column) => (
              <th key={column.id}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, rowIndex) => (
            <tr key={`row-${rowIndex}`}>
              {result.columns.map((column) => (
                <td key={column.id}>{String(row.values[column.id] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderResult(result: AnalysisQueryResponse, config: AnalysisViewConfig) {
  if (!result.columns.length || !result.rows.length) {
    return <div className="emptyState">Sem dados para essa composição.</div>;
  }

  const type = config.visualization.type;

  if (type === "table") {
    return <TableView result={result} />;
  }
  if (type === "bar") {
    return <BarChart result={result} orientation="bar" />;
  }
  if (type === "column") {
    return <BarChart result={result} orientation="column" />;
  }
  if (type === "line") {
    return <LineChart result={result} />;
  }
  if (type === "pie") {
    return <PieChart result={result} />;
  }

  return <div className="emptyState compact">Visualização não suportada.</div>;
}

function visualizationLabel(type: AnalysisViewConfig["visualization"]["type"]) {
  if (type === "table") {
    return "Tabela";
  }
  if (type === "line") {
    return "Linha";
  }
  if (type === "pie") {
    return "Pizza";
  }
  if (type === "column") {
    return "Colunas";
  }
  return "Barras";
}

function VizIcon({ type }: { type: AnalysisViewConfig["visualization"]["type"] }) {
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
  initialQuery,
  initialConfig,
  entityId,
}: {
  scopeLabel: string;
  initialQuery: AnalysisQueryResponse;
  initialConfig: AnalysisViewConfig;
  entityId?: string | null;
}) {
  return (
    <section className="panel canvasPanel">
      <div className="canvasHeader">
        <h3 className="canvasTitle">{scopeLabel}</h3>
        <div className="canvasMeta">
          <span className="statusPill">{visualizationLabel(initialConfig.visualization.type)}</span>
          <VizIcon type={initialConfig.visualization.type} />
        </div>
      </div>

      <div className="canvasBody">
        {entityId ? (
          <div className="entityFilterBanner">
            Filtrado por entidade: <strong>{entityId}</strong>
          </div>
        ) : null}
        {renderResult(initialQuery, initialConfig)}
      </div>
    </section>
  );
}
