export const assetCards = [
  { id: "TR-01", name: "TR-01", type: "Transformer", score: 72, status: "Warning" },
  { id: "GB-02", name: "GB-02", type: "Generator", score: 88, status: "Healthy" },
  { id: "DJ-03", name: "DJ-03", type: "Breaker", score: 39, status: "Critical" },
];

export const alerts = [
  { id: "AL-001", severity: "high", title: "Temperatura acima do limite", asset: "TR-01" },
  { id: "AL-002", severity: "critical", title: "Queda brusca de score", asset: "DJ-03" },
];

export const cases = [
  { id: "CS-001", title: "Investigar TR-01", status: "open", priority: "high" },
];
