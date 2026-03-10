import Link from "next/link";
import { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/sources", label: "Sources" },
  { href: "/datasets", label: "Datasets" },
  { href: "/graph", label: "Graph" },
  { href: "/insights", label: "Insights" },
  { href: "/copilot", label: "Copilot" },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">OntoGrid</p>
          <h1>Energy Data Hub</h1>
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
