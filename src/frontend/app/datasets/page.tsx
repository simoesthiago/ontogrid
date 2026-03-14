import Link from "next/link";

import { getDatasets } from "../../lib/api";
import {
  ENERGY_HUB_SOURCES,
  formatDateLabel,
  getQueryValue,
  titleCaseToken,
} from "../../lib/energy-hub";
import { buildPageHref, createSearchParams } from "../../lib/search-state";

export const dynamic = "force-dynamic";

export default async function DatasetsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolvedSearchParams = await searchParams;
  const query = getQueryValue(resolvedSearchParams.q)?.trim() ?? "";
  const sourceFilter = getQueryValue(resolvedSearchParams.source) ?? "all";
  const sort = getQueryValue(resolvedSearchParams.sort) ?? "name";
  const searchState = createSearchParams({
    q: query || undefined,
    source: sourceFilter !== "all" ? sourceFilter : undefined,
    sort: sort !== "name" ? sort : undefined,
  });

  const datasetsResponse = await getDatasets({
    limit: 400,
    q: query || undefined,
    source: sourceFilter !== "all" ? sourceFilter : undefined,
  });

  const datasets = [...datasetsResponse.items].sort((left, right) => {
    if (sort === "updated") {
      return (right.latest_published_at || "").localeCompare(left.latest_published_at || "");
    }
    if (sort === "source") {
      return `${left.source_code}-${left.name}`.localeCompare(`${right.source_code}-${right.name}`);
    }
    return left.name.localeCompare(right.name);
  });

  return (
    <div className="pageWorkspace">
      <div className="pageTitleBar">
        <h1 className="pageTitle">Datasets</h1>
      </div>

      <section className="panel">
        <div className="toolbar">
          <form action="/datasets" className="searchForm grow">
            <input type="hidden" name="source" value={sourceFilter} />
            <input type="hidden" name="sort" value={sort} />
            <input
              className="searchInput"
              type="search"
              name="q"
              defaultValue={query}
              placeholder="Buscar dataset por nome ou codigo"
              aria-label="Buscar dataset"
            />
          </form>

          <div className="toolbarActions">
            <Link
              href={buildPageHref("/datasets", searchState, {
                sort: sort === "updated" ? "name" : "updated",
              })}
              className="iconButton"
            >
              Ordenar
            </Link>
            <Link href={buildPageHref("/datasets", searchState, { sort: "source" })} className="iconButton">
              Fonte
            </Link>
          </div>
        </div>

        <div className="filterChips">
          {ENERGY_HUB_SOURCES.map((source) => (
            <Link
              key={source.id}
              href={buildPageHref("/datasets", searchState, {
                source: source.id === "all" ? undefined : source.id,
              })}
              className={`filterChip ${sourceFilter === source.id ? "isSelected" : ""}`}
            >
              {source.label}
            </Link>
          ))}
        </div>

        <div className="tableWrap">
          <table className="dataTable">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Grupo</th>
                <th>Fonte</th>
                <th>Ultima atualizacao</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {datasets.length ? (
                datasets.map((dataset) => (
                  <tr key={dataset.id}>
                    <td>
                      <Link href={`/datasets/${dataset.id}`} className="tablePrimaryLink">
                        {dataset.name}
                      </Link>
                      <div className="tableSecondary">{dataset.code}</div>
                      <div className="tableActionRow">
                        <Link href={`/analysis?dataset=${dataset.id}`} className="tableActionLink">
                          Analisar
                        </Link>
                      </div>
                    </td>
                    <td>{titleCaseToken(dataset.domain)}</td>
                    <td>{dataset.source_code.toUpperCase()}</td>
                    <td>{formatDateLabel(dataset.latest_published_at)}</td>
                    <td>
                      <span className={`statusPill ${dataset.ingestion_status === "published" ? "" : "mutedPill"}`}>
                        {dataset.ingestion_status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5}>
                    <div className="emptyState">Nenhum dataset encontrado com os filtros atuais.</div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
