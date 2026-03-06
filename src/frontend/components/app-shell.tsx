import Link from "next/link";
import { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/assets", label: "Assets" },
  { href: "/alerts", label: "Alerts" },
  { href: "/cases", label: "Cases" },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">OntoGrid</p>
          <h1>MVP v0.1</h1>
        </div>
        <nav>
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="navLink">
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
