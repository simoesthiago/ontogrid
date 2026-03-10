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
  version_id: string;
  entity_id?: string | null;
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
