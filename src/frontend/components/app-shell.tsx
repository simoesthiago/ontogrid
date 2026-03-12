"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

const navGroups = [
  {
    label: "Mission Control",
    items: [
      { href: "/", label: "Overview" },
      { href: "/coverage", label: "Coverage" },
      { href: "/sources", label: "Sources" },
    ],
  },
  {
    label: "Data Plane",
    items: [
      { href: "/datasets", label: "Datasets" },
      { href: "/graph", label: "Graph" },
      { href: "/insights", label: "Insights" },
    ],
  },
  {
    label: "Reasoning",
    items: [{ href: "/copilot", label: "Copilot" }],
  },
];

const routeMeta: Record<string, { eyebrow: string; title: string; detail: string }> = {
  "/": {
    eyebrow: "Mission Control",
    title: "Public energy intelligence",
    detail: "Catalog, provenance and graph context in one operating surface.",
  },
  "/coverage": {
    eyebrow: "Catalog Coverage",
    title: "Documentation versus live runtime",
    detail: "Track the gap between mapped datasets and executable pipelines.",
  },
  "/sources": {
    eyebrow: "Source Registry",
    title: "Public authorities and refresh posture",
    detail: "Monitor the shape, cadence and current health of each source.",
  },
  "/datasets": {
    eyebrow: "Dataset Fleet",
    title: "Traceable data products",
    detail: "Navigate the hub by dataset, status and publication depth.",
  },
  "/graph": {
    eyebrow: "Semantic Layer",
    title: "Canonical sector entities",
    detail: "Inspect reconciled objects, aliases and graph neighborhoods.",
  },
  "/insights": {
    eyebrow: "Analytic Layer",
    title: "Grounded signal snapshots",
    detail: "Read the latest derived signals backed by published versions.",
  },
  "/copilot": {
    eyebrow: "Reasoning Layer",
    title: "Grounded copilot console",
    detail: "Ask questions against the public hub and audit the evidence path.",
  },
};

function isActive(pathname: string, href: string) {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

function resolveRouteMeta(pathname: string) {
  const directMatch = routeMeta[pathname];
  if (directMatch) {
    return directMatch;
  }

  if (pathname.startsWith("/datasets/")) {
    return {
      eyebrow: "Dataset Detail",
      title: "Versioned dataset inspection",
      detail: "Inspect schema, versions, observations and pipeline telemetry.",
    };
  }

  if (pathname.startsWith("/entities/")) {
    return {
      eyebrow: "Entity Profile",
      title: "Canonical entity lens",
      detail: "Inspect identity, series, graph relations and published evidence.",
    };
  }

  return routeMeta["/"];
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const current = resolveRouteMeta(pathname);
  const today = new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date());

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brandBlock">
          <div className="brandMark">OG</div>
          <div className="stackCompact">
            <p className="eyebrow">OntoGrid</p>
            <h1>Energy Data Hub</h1>
            <p className="muted">
              Public-first operating surface for the Brazilian power sector.
            </p>
          </div>
        </div>

        <div className="sidebarSection">
          {navGroups.map((group) => (
            <div key={group.label} className="stackCompact">
              <p className="navSectionLabel">{group.label}</p>
              <nav className="navStack">
                {group.items.map((item) => {
                  const active = isActive(pathname, item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="navLink"
                      aria-current={active ? "page" : undefined}
                    >
                      <span>{item.label}</span>
                      <span className="navHint">{item.href === "/" ? "root" : item.href.slice(1)}</span>
                    </Link>
                  );
                })}
              </nav>
            </div>
          ))}
        </div>

        <div className="sidebarSection sidebarTelemetry">
          <p className="navSectionLabel">System Posture</p>
          <div className="surfaceStat">
            <span className="surfaceStatLabel">Runtime</span>
            <strong>Local compose</strong>
          </div>
          <div className="surfaceStat">
            <span className="surfaceStatLabel">Contract</span>
            <strong>REST only</strong>
          </div>
          <div className="surfaceStat">
            <span className="surfaceStatLabel">Graph</span>
            <strong>Neo4j enabled</strong>
          </div>
        </div>
      </aside>

      <div className="shellMain">
        <header className="topbar">
          <div className="stackCompact">
            <p className="eyebrow">{current.eyebrow}</p>
            <div className="topbarRow">
              <h2 className="topbarTitle">{current.title}</h2>
              <span className="topbarDate">{today}</span>
            </div>
            <p className="muted">{current.detail}</p>
          </div>
          <div className="topbarPills">
            <span className="pill healthy">Public data live</span>
            <span className="pill">Brazil power domain</span>
            <span className="pill warning">Decision support</span>
          </div>
        </header>

        <main className="content">
          <div className="contentInner">{children}</div>
        </main>
      </div>
    </div>
  );
}
