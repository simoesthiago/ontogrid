import type { AnalysisFieldsResponse, AnalysisViewConfig } from "./api";

export function buildDefaultViewConfig(
  fields: AnalysisFieldsResponse,
  datasetId: string,
  entityId?: string | null,
): AnalysisViewConfig {
  const firstDimension = fields.dimensions[0]?.id;
  const defaultMeasure = fields.default_measure ?? fields.metrics[0]?.field ?? "";

  return {
    dataset_id: datasetId,
    entity_id: entityId ?? null,
    rows: firstDimension ? [firstDimension] : [],
    columns: [],
    filters: [],
    measures: defaultMeasure ? [{ field: defaultMeasure, aggregation: "sum" }] : [],
    visualization: { type: "table" },
  };
}
