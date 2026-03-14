export type SearchStateValue = string | null | undefined;

export function createSearchParams(values: Record<string, SearchStateValue>): URLSearchParams {
  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(values)) {
    if (value) {
      params.set(key, value);
    }
  }

  return params;
}

export function buildPageHref(
  pathname: string,
  current: URLSearchParams,
  updates: Record<string, SearchStateValue>,
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
  return query ? `${pathname}?${query}` : pathname;
}
