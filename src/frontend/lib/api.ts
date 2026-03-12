const API_BASE =
  process.env.API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000/api/v1";

export interface SourceItem {
  id: string;
  code: string;
  name: string;
  authority_type: string;
  refresh_strategy: string;
  status: string;
}

export interface SourceListResponse {
  items: SourceItem[];
  total: number;
}

export interface DatasetListItem {
  id: string;
  source_code: string;
  code: string;
  name: string;
  domain: string;
  granularity: string;
  latest_version: string;
  latest_published_at: string;
  freshness_status: string;
  adapter_enabled: boolean;
  ingestion_status: string;
}

export interface DatasetListResponse {
  items: DatasetListItem[];
  total: number;
}

export interface DatasetVersionSummary {
  id: string;
  label: string;
  published_at: string;
}

export interface DatasetDetailResponse {
  id: string;
  source_id: string;
  source_code: string;
  code: string;
  name: string;
  domain: string;
  description: string;
  granularity: string;
  refresh_frequency: string;
  schema_summary: Record<string, unknown>;
  latest_version: DatasetVersionSummary;
  adapter_enabled: boolean;
  ingestion_status: string;
}

export interface DatasetVersionItem {
  id: string;
  label: string;
  extracted_at: string;
  published_at: string;
  coverage_start?: string | null;
  coverage_end?: string | null;
  status: string;
  checksum: string;
}

export interface DatasetVersionListResponse {
  dataset_id: string;
  items: DatasetVersionItem[];
}

export interface DatasetVersionDetailResponse extends DatasetVersionItem {
  dataset_id: string;
  row_count: number;
  schema_version: string;
  lineage: Record<string, unknown>;
}

export interface GraphEntityItem {
  id: string;
  entity_type: string;
  canonical_code: string;
  name: string;
  aliases: string[];
  jurisdiction: string;
}

export interface GraphEntityListResponse {
  items: GraphEntityItem[];
  total: number;
}

export interface GraphNode {
  id: string;
  type: string;
  name: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GraphNeighborsResponse {
  entity_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  provenance: {
    dataset_version_ids: string[];
  };
}

export interface InsightCard {
  id: string;
  title: string;
  value: number;
  unit: string;
  trend: string;
}

export interface InsightHighlight {
  title: string;
  dataset_version_id: string;
}

export interface InsightOverviewResponse {
  cards: InsightCard[];
  highlights: InsightHighlight[];
}

export interface CatalogCoverageSourceItem {
  source_code: string;
  source_name: string;
  source_document: string;
  inventoried_total: number;
  documented_only_total: number;
  adapter_enabled_total: number;
  published_total: number;
}

export interface CatalogCoverageFamilyItem {
  source_code: string;
  family: string;
  inventoried_total: number;
  documented_only_total: number;
  adapter_enabled_total: number;
  published_total: number;
}

export interface CatalogCoverageResponse {
  inventoried_total: number;
  documented_only_total: number;
  adapter_enabled_total: number;
  published_total: number;
  sources: CatalogCoverageSourceItem[];
  families: CatalogCoverageFamilyItem[];
}

export interface CopilotCitation {
  source_code: string;
  dataset_id: string;
  dataset_code: string;
  dataset_name: string;
  version_id: string;
  version_label: string;
  entity_id?: string | null;
  entity_name?: string | null;
  evidence_id?: string | null;
}

export interface CopilotQueryRequest {
  question: string;
  dataset_ids?: string[];
  entity_ids?: string[];
  start?: string;
  end?: string;
  locale?: string;
}

export interface CopilotQueryResponse {
  answer: string;
  citations: CopilotCitation[];
  follow_up_questions: string[];
}

export interface EntityProfileAlias {
  source_code: string;
  alias_name: string;
  external_code?: string | null;
  confidence?: number | null;
}

export interface EntityProfileSeriesItem {
  series_id: string;
  dataset_id: string;
  dataset_code: string;
  metric_code: string;
  metric_name: string;
  unit: string;
  temporal_granularity: string;
  semantic_value_type: string;
  reference_time_kind: string;
  latest_observation_at: string;
  latest_value: number | string | null;
}

export interface EntityProfileVersionItem {
  dataset_version_id: string;
  label: string;
  published_at?: string | null;
  dataset_id: string;
  dataset_code: string;
}

export interface EntityProfileEvidenceItem {
  id: string;
  scope_type: string;
  scope_id: string;
  dataset_version_id: string;
  series_id?: string | null;
  selector: Record<string, unknown>;
  claim_text: string;
  created_at?: string | null;
}

export interface EntityProfileResponse {
  identity: {
    id: string;
    entity_type: string;
    canonical_code: string;
    name: string;
    jurisdiction: string;
    attributes: Record<string, unknown>;
  };
  aliases: EntityProfileAlias[];
  semantic_type: string;
  facets: {
    party?: Record<string, unknown> | null;
    agent_profile: Record<string, unknown>[];
    generation_asset?: Record<string, unknown> | null;
    geo: Record<string, unknown>[];
    regulatory?: Record<string, unknown> | null;
  };
  series: EntityProfileSeriesItem[];
  neighbors: GraphNeighborsResponse | null;
  recent_versions: EntityProfileVersionItem[];
  evidence: EntityProfileEvidenceItem[];
  graph_status: string;
}

export interface SeriesListItem {
  id: string;
  dataset_id: string;
  metric_code: string;
  metric_name: string;
  unit: string;
  temporal_granularity: string;
  entity_type: string;
  latest_observation_at: string;
  semantic_value_type: string;
  reference_time_kind: string;
}

export interface SeriesListResponse {
  items: SeriesListItem[];
  total: number;
}

export interface ObservationItem {
  entity_id: string;
  entity_name: string;
  timestamp: string;
  value: number | string | null;
  unit: string;
  quality_flag: string;
  published_at: string;
}

export interface ObservationListResponse {
  series_id: string;
  dataset_version_id: string;
  items: ObservationItem[];
}

export interface RefreshJobItem {
  id: string;
  dataset_id: string;
  dataset_code: string;
  dataset_name: string;
  source_code: string;
  trigger_type: string;
  status: string;
  rows_read: number;
  rows_written: number;
  error_summary?: string | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  published_version_id?: string | null;
  published_version_label?: string | null;
}

export interface RefreshJobListResponse {
  items: RefreshJobItem[];
  total: number;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate: 60 },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function getSources(params?: {
  q?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<SourceListResponse> {
  const qs = new URLSearchParams();
  if (params?.q) qs.set("q", params.q);
  if (params?.status) qs.set("status", params.status);
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<SourceListResponse>(`/sources${query}`);
}

export async function getDatasets(params?: {
  source?: string;
  domain?: string;
  granularity?: string;
  q?: string;
  limit?: number;
  offset?: number;
}): Promise<DatasetListResponse> {
  const qs = new URLSearchParams();
  if (params?.source) qs.set("source", params.source);
  if (params?.domain) qs.set("domain", params.domain);
  if (params?.granularity) qs.set("granularity", params.granularity);
  if (params?.q) qs.set("q", params.q);
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<DatasetListResponse>(`/datasets${query}`);
}

export async function getDataset(datasetId: string): Promise<DatasetDetailResponse> {
  return apiFetch<DatasetDetailResponse>(`/datasets/${datasetId}`);
}

export async function getDatasetVersions(datasetId: string): Promise<DatasetVersionListResponse> {
  return apiFetch<DatasetVersionListResponse>(`/datasets/${datasetId}/versions`);
}

export async function getDatasetVersion(
  datasetId: string,
  versionId: string,
): Promise<DatasetVersionDetailResponse> {
  return apiFetch<DatasetVersionDetailResponse>(`/datasets/${datasetId}/versions/${versionId}`);
}

export async function getGraphEntities(params?: {
  q?: string;
  entity_type?: string;
  source?: string;
  limit?: number;
  offset?: number;
}): Promise<GraphEntityListResponse> {
  const qs = new URLSearchParams();
  if (params?.q) qs.set("q", params.q);
  if (params?.entity_type) qs.set("entity_type", params.entity_type);
  if (params?.source) qs.set("source", params.source);
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<GraphEntityListResponse>(`/graph/entities${query}`);
}

export async function getEntityNeighbors(entityId: string): Promise<GraphNeighborsResponse> {
  return apiFetch<GraphNeighborsResponse>(`/graph/entities/${entityId}/neighbors`);
}

export async function getEntityProfile(entityId: string): Promise<EntityProfileResponse> {
  return apiFetch<EntityProfileResponse>(`/entities/${entityId}/profile`);
}

export async function getInsightsOverview(params?: {
  domain?: string;
  period?: string;
}): Promise<InsightOverviewResponse> {
  const qs = new URLSearchParams();
  if (params?.domain) qs.set("domain", params.domain);
  if (params?.period) qs.set("period", params.period);
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<InsightOverviewResponse>(`/insights/overview${query}`);
}

export async function getCatalogCoverage(): Promise<CatalogCoverageResponse> {
  return apiFetch<CatalogCoverageResponse>("/catalog/coverage");
}

export async function getSeries(params?: {
  dataset_id?: string;
  entity_id?: string;
  metric_code?: string;
  q?: string;
  limit?: number;
  offset?: number;
}): Promise<SeriesListResponse> {
  const qs = new URLSearchParams();
  if (params?.dataset_id) qs.set("dataset_id", params.dataset_id);
  if (params?.entity_id) qs.set("entity_id", params.entity_id);
  if (params?.metric_code) qs.set("metric_code", params.metric_code);
  if (params?.q) qs.set("q", params.q);
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<SeriesListResponse>(`/series${query}`);
}

export async function getSeriesObservations(
  seriesId: string,
  params?: {
    start?: string;
    end?: string;
    dataset_version_id?: string;
    entity_id?: string;
    limit?: number;
    offset?: number;
  },
): Promise<ObservationListResponse> {
  const qs = new URLSearchParams();
  if (params?.start) qs.set("start", params.start);
  if (params?.end) qs.set("end", params.end);
  if (params?.dataset_version_id) qs.set("dataset_version_id", params.dataset_version_id);
  if (params?.entity_id) qs.set("entity_id", params.entity_id);
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<ObservationListResponse>(`/series/${seriesId}/observations${query}`);
}

export async function getRefreshJobs(params?: {
  dataset_id?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<RefreshJobListResponse> {
  const qs = new URLSearchParams();
  if (params?.dataset_id) qs.set("dataset_id", params.dataset_id);
  if (params?.status) qs.set("status", params.status);
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<RefreshJobListResponse>(`/admin/refresh-jobs${query}`);
}

export async function queryCopilot(payload: CopilotQueryRequest): Promise<CopilotQueryResponse> {
  const res = await fetch(`${API_BASE}/copilot/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let detail = `API error ${res.status} on /copilot/query`;
    try {
      const errorPayload = (await res.json()) as { detail?: string };
      if (errorPayload.detail) {
        detail = errorPayload.detail;
      }
    } catch {
      // Preserve the fallback error message when the response is not JSON.
    }
    throw new Error(detail);
  }
  return res.json() as Promise<CopilotQueryResponse>;
}
