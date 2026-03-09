export const sourceCards = [
  { id: "aneel", name: "ANEEL", type: "Regulador", status: "Ativa", strategy: "Scheduled download" },
  { id: "ons", name: "ONS", type: "Operador do sistema", status: "Ativa", strategy: "Scheduled download" },
  { id: "ccee", name: "CCEE", type: "Operador de mercado", status: "Ativa", strategy: "Scheduled download" },
];

export const datasetCards = [
  {
    id: "ds-ons-carga",
    source: "ONS",
    name: "Carga horaria por submercado",
    domain: "Operacao",
    granularity: "Hora",
    version: "2026-03-09",
  },
  {
    id: "ds-aneel-tarifas",
    source: "ANEEL",
    name: "Tarifas homologadas de distribuicao",
    domain: "Regulatorio",
    granularity: "Mes",
    version: "2026-03",
  },
  {
    id: "ds-ccee-pld",
    source: "CCEE",
    name: "PLD horario por submercado",
    domain: "Mercado",
    granularity: "Hora",
    version: "2026-03-09",
  },
];

export const graphEntities = [
  { id: "ent-se-co", name: "Sudeste/Centro-Oeste", type: "Submercado", source: "ONS" },
  { id: "ent-nordeste", name: "Nordeste", type: "Submercado", source: "ONS" },
  { id: "ent-enel-sp", name: "Enel SP", type: "Distribuidora", source: "ANEEL" },
];

export const insightCards = [
  {
    title: "Cobertura publica inicial",
    body: "O scaffold ja separa fontes, datasets, versoes e entidades para ANEEL, ONS e CCEE.",
  },
  {
    title: "Contrato REST-first",
    body: "O frontend agora aponta para catalogo, series e graph, sem depender de tenant_id.",
  },
  {
    title: "Proximo passo natural",
    body: "Trocar os mocks por leitura real em Postgres, TimescaleDB e Neo4j.",
  },
];
