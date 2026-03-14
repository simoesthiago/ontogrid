"use client";

import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { ENERGY_HUB_SOURCES } from "../../lib/energy-hub";

export function SearchForm({
  query,
  sourceFilter,
}: {
  query: string;
  sourceFilter: string;
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function selectSource(sourceId: string) {
    setOpen(false);
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    if (sourceId !== "all") params.set("source", sourceId);
    const qs = params.toString();
    router.push(qs ? `/analysis?${qs}` : "/analysis");
  }

  const isFiltered = sourceFilter !== "all";

  return (
    <form action="/analysis" className="searchForm">
      <input
        className="searchInput"
        type="search"
        name="q"
        defaultValue={query}
        placeholder="Buscar dataset"
        aria-label="Buscar dataset"
      />
      <div ref={ref} className="filterDropdown">
        <button
          type="button"
          className={`iconButton filterIconButton${isFiltered ? " isActive" : ""}`}
          onClick={() => setOpen((v) => !v)}
          aria-label="Filtrar por fonte"
          title={isFiltered ? `Fonte: ${sourceFilter.toUpperCase()}` : "Filtrar por fonte"}
        >
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M1.5 3h13M4 8h8M6.5 13h3" />
          </svg>
        </button>
        {open && (
          <div className="filterDropdownMenu">
            {ENERGY_HUB_SOURCES.map((source) => (
              <button
                key={source.id}
                type="button"
                className={`filterDropdownItem${sourceFilter === source.id ? " isActive" : ""}`}
                onClick={() => selectSource(source.id)}
              >
                {source.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </form>
  );
}
