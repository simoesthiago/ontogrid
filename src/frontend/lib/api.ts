// Cliente de API server-side para Server Components Next.js
// Usa API_BASE_URL (variavel de servidor, sem NEXT_PUBLIC_)

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000/api/v1";

// ---------- Types ----------

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
}

export interface DatasetListResponse {
  items: DatasetListItem[];
  total: number;
}

// ---------- Helpers ----------

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate: 60 }, // revalida a cada 60s
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

// ---------- Sources ----------

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

// ---------- Datasets ----------

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
