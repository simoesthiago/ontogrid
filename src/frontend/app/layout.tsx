import "./globals.css";

import { AppShell } from "../components/app-shell";
import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "OntoGrid",
  description: "Energy Data Hub publico para o setor eletrico brasileiro",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
