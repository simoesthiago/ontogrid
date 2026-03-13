"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

const energyHubLinks = [
  { href: "/analysis", label: "Analysis" },
  { href: "/entities", label: "Entidades" },
  { href: "/datasets", label: "Datasets" },
];

const supportLinks = [{ href: "/settings", label: "Configuracoes" }];

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebarTop">
          <Link href="/analysis" className="brandLink">
            <span className="brandTitle">Ontogrid</span>
          </Link>

          <section className="sidebarBlock">
            <p className="sidebarLabel">Apps</p>

            <div className="appSection">
              <div className="appSectionHeader">
                <span className="appSectionTitle">Energy Hub</span>
                <span className="appSectionTag">ativo</span>
              </div>
              <nav className="navStack">
                {energyHubLinks.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="navLink"
                    aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>

            <div className="appFutureBlock">
              <p className="appFutureTitle">Enterprise Apps</p>
              <p className="muted">Entram depois, sem poluir o Energy Hub agora.</p>
            </div>
          </section>
        </div>

        <div className="sidebarBottom">
          <section className="sidebarBlock">
            <p className="sidebarLabel">Workspace</p>
            <nav className="navStack">
              {supportLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="navLink"
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </section>
        </div>
      </aside>

      <main className="shellMain">
        <div className="content">
          <div className="contentInner">{children}</div>
        </div>
      </main>
    </div>
  );
}
