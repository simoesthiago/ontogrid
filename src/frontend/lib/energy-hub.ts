export const ENERGY_HUB_ENTITY_TYPES = [
  { id: "agent", label: "Agente", description: "participante economico-regulatorio" },
  { id: "distributor", label: "Distribuidora", description: "operadora de distribuicao e qualidade" },
  { id: "plant", label: "Usina", description: "ativo de geracao" },
  { id: "submarket", label: "Submercado", description: "recorte geografico-eletrico" },
  { id: "reservoir", label: "Reservatorio", description: "ativo hidrico" },
] as const;

export const ENERGY_HUB_SOURCES = [
  { id: "all", label: "Todas as fontes" },
  { id: "aneel", label: "ANEEL" },
  { id: "ons", label: "ONS" },
  { id: "ccee", label: "CCEE" },
] as const;

export function getQueryValue(
  value: string | string[] | undefined,
): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

export function formatDateLabel(value?: string | null): string {
  if (!value) {
    return "Sem publicacao";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function titleCaseToken(value: string): string {
  if (!value) {
    return value;
  }

  return value
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(" ");
}

export function slugifyLabel(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}
