from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / "src" / "backend"))

from app.catalog_inventory import get_dataset_seeds  # noqa: E402


def load_adapter_codes() -> set[str]:
    registry_path = REPO_ROOT / "src" / "backend" / "app" / "ingestion" / "registry.py"
    module = ast.parse(registry_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_ADAPTERS":
                    if not isinstance(node.value, ast.Dict):
                        raise ValueError("_ADAPTERS must remain a dictionary literal")
                    codes: set[str] = set()
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            codes.add(key.value)
                    return codes
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "_ADAPTERS":
            if not isinstance(node.value, ast.Dict):
                raise ValueError("_ADAPTERS must remain a dictionary literal")
            codes: set[str] = set()
            for key in node.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    codes.add(key.value)
            return codes
    raise ValueError("Could not locate _ADAPTERS in ingestion registry")


def build_catalog_snapshot() -> dict[str, object]:
    source_order = ["aneel", "ons", "ccee"]
    seeds = sorted(get_dataset_seeds(), key=lambda item: (source_order.index(item.source_code), item.domain, item.name))
    adapter_codes = load_adapter_codes()
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    by_source: dict[str, dict[str, int | str]] = {}
    adapter_datasets: list[dict[str, str]] = []
    items: list[dict[str, object]] = []

    for seed in seeds:
        source_entry = by_source.setdefault(
            seed.source_code,
            {
                "source_code": seed.source_code,
                "inventariado": 0,
                "catalogado": 0,
                "adapter_pronto": 0,
                "pendente_adapter": 0,
            },
        )
        source_entry["inventariado"] += 1
        source_entry["catalogado"] += 1

        adapter_ready = seed.code in adapter_codes
        if adapter_ready:
            source_entry["adapter_pronto"] += 1
            adapter_datasets.append(
                {
                    "source_code": seed.source_code,
                    "dataset_code": seed.code,
                    "dataset_name": seed.name,
                    "family": seed.domain,
                }
            )
        else:
            source_entry["pendente_adapter"] += 1

        items.append(
            {
                "source_code": seed.source_code,
                "dataset_code": seed.code,
                "dataset_name": seed.name,
                "family": seed.domain,
                "inventariado": True,
                "catalogado": True,
                "adapter_pronto": adapter_ready,
                "publicado": "environment_dependent",
                "repo_stage": "adapter_pronto" if adapter_ready else "catalogado",
            }
        )

    sources = sorted(by_source.values(), key=lambda item: source_order.index(str(item["source_code"])))
    adapter_datasets.sort(key=lambda item: (source_order.index(str(item["source_code"])), str(item["dataset_name"])))
    total_inventory = len(seeds)
    total_adapter_ready = len(adapter_datasets)

    return {
        "generated_at": generated_at,
        "inventory_sources": [
            "docs/datasets/datasets_ANEEL.md",
            "docs/datasets/datasets_ONS.md",
            "docs/datasets/datasets_CCEE.md",
        ],
        "taxonomy": {
            "inventariado": "Dataset apareceu no levantamento da fonte.",
            "catalogado": "Dataset entrou no catalogo do app/repo.",
            "adapter_pronto": "Dataset ja possui adapter implementado no repo.",
            "publicado": "Estado operacional do ambiente; nao e um snapshot estatico do git.",
        },
        "repo_snapshot": {
            "inventariado": total_inventory,
            "catalogado": total_inventory,
            "adapter_pronto": total_adapter_ready,
            "pendente_adapter": total_inventory - total_adapter_ready,
            "publicado": "use_runtime_coverage_endpoint",
        },
        "sources": sources,
        "adapter_datasets": adapter_datasets,
        "items": items,
    }


def build_markdown(snapshot: dict[str, object]) -> str:
    sources = snapshot["sources"]
    adapter_datasets = snapshot["adapter_datasets"]
    repo_snapshot = snapshot["repo_snapshot"]

    lines = [
        "# Catalog Status - OntoGrid",
        "",
        "- Status: fonte oficial legivel para humanos do catalogo do repo",
        "- Manifest machine-readable correspondente: `docs/datasets/catalog_status.json`",
        "- Regra: `publicado` e estado operacional do ambiente e deve ser lido via `/api/v1/catalog/coverage`, nao como snapshot estatico do git",
        "",
        "## Resumo do repo",
        "",
        f"- Inventariados: **{repo_snapshot['inventariado']}**",
        f"- Catalogados: **{repo_snapshot['catalogado']}**",
        f"- Adapters prontos: **{repo_snapshot['adapter_pronto']}**",
        f"- Pendentes de adapter: **{repo_snapshot['pendente_adapter']}**",
        "",
        "## Breakdown por fonte",
        "",
        "| Fonte | Inventariados | Catalogados | Adapter pronto | Pendente de adapter |",
        "|---|---:|---:|---:|---:|",
    ]

    for source in sources:
        lines.append(
            f"| {str(source['source_code']).upper()} | {source['inventariado']} | {source['catalogado']} | "
            f"{source['adapter_pronto']} | {source['pendente_adapter']} |"
        )

    lines.extend(
        [
            "",
            "## Taxonomia oficial",
            "",
            "- `inventariado`: apareceu no levantamento da fonte.",
            "- `catalogado`: entrou no catalogo do app/repo.",
            "- `adapter_pronto`: ja possui adapter implementado no repo.",
            "- `publicado`: ja possui versao publicada em um ambiente operacional e deve ser lido via `/api/v1/catalog/coverage`.",
            "",
            "## Datasets com adapter pronto no repo",
            "",
            "| Fonte | Dataset code | Dataset | Familia |",
            "|---|---|---|---|",
        ]
    )

    for item in adapter_datasets:
        lines.append(
            f"| {str(item['source_code']).upper()} | `{item['dataset_code']}` | {item['dataset_name']} | {item['family']} |"
        )

    lines.extend(
        [
            "",
            "## Regra de leitura",
            "",
            "- Os **345 datasets** ja aparecem no catalogo do produto como universo mapeado do repo.",
            "- Nem todo dataset catalogado possui ingestao implementada hoje.",
            "- O runtime local deve operar com `catalog` ou `sample` por padrao; ingestao live pesada fica para uso explicito ou ambiente central.",
            "- `publicado` varia por ambiente porque depende do banco e dos refresh jobs daquele runtime.",
            "",
            "## Como regenerar",
            "",
            "```powershell",
            "python scripts/generate_catalog_status.py",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    snapshot = build_catalog_snapshot()
    json_path = REPO_ROOT / "docs" / "datasets" / "catalog_status.json"
    md_path = REPO_ROOT / "docs" / "datasets" / "CATALOG_STATUS.md"

    json_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(snapshot), encoding="utf-8")


if __name__ == "__main__":
    main()
