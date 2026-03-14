"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useState } from "react";

const energyHubLinks = [
  {
    href: "/analysis",
    label: "Analysis",
    icon: (
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <rect x="1" y="8" width="3" height="7" fill="currentColor" />
        <rect x="6" y="5" width="3" height="10" fill="currentColor" />
        <rect x="11" y="2" width="3" height="13" fill="currentColor" />
      </svg>
    ),
  },
  {
    href: "/entities",
    label: "Entidades",
    icon: (
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5" />
        <ellipse cx="8" cy="8" rx="2.5" ry="6.5" stroke="currentColor" strokeWidth="1.5" />
        <line x1="1.5" y1="6" x2="14.5" y2="6" stroke="currentColor" strokeWidth="1.5" />
        <line x1="1.5" y1="10" x2="14.5" y2="10" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    ),
  },
  {
    href: "/datasets",
    label: "Datasets",
    icon: (
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <ellipse cx="8" cy="4" rx="6" ry="2" stroke="currentColor" strokeWidth="1.5" />
        <path d="M2 4v4c0 1.1 2.69 2 6 2s6-.9 6-2V4" stroke="currentColor" strokeWidth="1.5" />
        <path d="M2 8v4c0 1.1 2.69 2 6 2s6-.9 6-2V8" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    ),
  },
  {
    href: "/copilot",
    label: "Copilot",
    icon: (
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <rect x="3" y="4" width="10" height="8" rx="2.5" stroke="currentColor" strokeWidth="1.5" />
        <path d="M8 1.5v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M5.5 8h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="5.5" cy="6.5" r=".75" fill="currentColor" />
        <circle cx="10.5" cy="6.5" r=".75" fill="currentColor" />
        <path d="M6 12.5v2l2-1.5 2 1.5v-2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

const supportLinks = [
  {
    href: "/settings",
    label: "Configurações",
    icon: (
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.5" />
        <path
          d="M8 1.5A6.5 6.5 0 0 1 9.6 2l.6 1.4a5 5 0 0 1 1.4.82l1.5-.3A6.5 6.5 0 0 1 14.5 6l-1 1.1a5 5 0 0 1 0 1.8l1 1.1a6.5 6.5 0 0 1-.9 2.08l-1.5-.3a5 5 0 0 1-1.4.82L10 14a6.5 6.5 0 0 1-4 0l-.6-1.4a5 5 0 0 1-1.4-.82l-1.5.3A6.5 6.5 0 0 1 1.5 10l1-1.1a5 5 0 0 1 0-1.8L1.5 6a6.5 6.5 0 0 1 .9-2.08l1.5.3A5 5 0 0 1 5.4 3.4L6 2A6.5 6.5 0 0 1 8 1.5Z"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
];

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`shell${collapsed ? " sidebarCollapsed" : ""}`}>
      <aside className={`sidebar${collapsed ? " isCollapsed" : ""}`}>
        <div className="sidebarTop">
          <div className="brandLink">
            <Link href="/analysis" className="brandTitle">
              {!collapsed && "Ontogrid"}
            </Link>
            <button
              className="sidebarToggle"
              onClick={() => setCollapsed((c) => !c)}
              aria-label={collapsed ? "Expandir sidebar" : "Minimizar sidebar"}
            >
              <svg width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <rect x="1" y="1" width="14" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.5" />
                <line x1="5.5" y1="1" x2="5.5" y2="15" stroke="currentColor" strokeWidth="1.5" />
              </svg>
            </button>
          </div>

          <div className="sidebarBlock">
            {!collapsed && <p className="sidebarLabel">Energy Hub</p>}
            <nav className="navStack">
              {energyHubLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="navLink"
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  title={collapsed ? item.label : undefined}
                >
                  {item.icon}
                  {!collapsed && <span className="navLinkLabel">{item.label}</span>}
                </Link>
              ))}
            </nav>
          </div>
        </div>

        <div className="sidebarBottom">
          <div className="sidebarBlock">
            {!collapsed && <p className="sidebarLabel">Suporte</p>}
            <nav className="navStack">
              {supportLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="navLink"
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  title={collapsed ? item.label : undefined}
                >
                  {item.icon}
                  {!collapsed && <span className="navLinkLabel">{item.label}</span>}
                </Link>
              ))}
            </nav>
          </div>
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
