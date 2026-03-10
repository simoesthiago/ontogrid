from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


@dataclass(frozen=True)
class CatalogSourceDefinition:
    id: str
    code: str
    name: str
    authority_type: str
    refresh_strategy: str
    status: str
    doc_path: Path


@dataclass(frozen=True)
class CatalogDatasetSeed:
    id: str
    source_id: str
    source_code: str
    code: str
    name: str
    domain: str
    description: str
    granularity: str
    refresh_frequency: str
    schema_summary: dict[str, list[str]]


_REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCE_DEFINITIONS: tuple[CatalogSourceDefinition, ...] = (
    CatalogSourceDefinition(
        id="src-aneel",
        code="aneel",
        name="ANEEL",
        authority_type="regulator",
        refresh_strategy="scheduled_download",
        status="active",
        doc_path=_REPO_ROOT / "docs" / "datasets" / "datasets_ANEEL.md",
    ),
    CatalogSourceDefinition(
        id="src-ons",
        code="ons",
        name="ONS",
        authority_type="system_operator",
        refresh_strategy="scheduled_download",
        status="active",
        doc_path=_REPO_ROOT / "docs" / "datasets" / "datasets_ONS.md",
    ),
    CatalogSourceDefinition(
        id="src-ccee",
        code="ccee",
        name="CCEE",
        authority_type="market_operator",
        refresh_strategy="scheduled_download",
        status="active",
        doc_path=_REPO_ROOT / "docs" / "datasets" / "datasets_CCEE.md",
    ),
)

_DATASET_OVERRIDES = {
    ("ons", "curva-de-carga-horaria"): {
        "id": "ds-ons-carga",
        "code": "carga_horaria_submercado",
        "name": "Carga horaria por submercado",
        "domain": "Carga, balanco e programacao",
        "description": "Serie horaria curada a partir do portal publico do ONS.",
        "granularity": "hour",
        "refresh_frequency": "daily",
        "schema_summary": {"dimensions": ["submarket"], "metrics": ["load_mw"]},
    },
    ("aneel", "tarifas-de-aplicacao-das-distribuidoras-de-energia-eletrica"): {
        "id": "ds-aneel-tarifas",
        "code": "tarifas_distribuicao",
        "name": "Tarifas homologadas de distribuicao",
        "domain": "Tarifas, mercado e subsidios",
        "description": "Base publica harmonizada de tarifas e ciclos homologatorios.",
        "granularity": "month",
        "refresh_frequency": "monthly",
        "schema_summary": {"dimensions": ["distributor"], "metrics": ["tariff_rs_mwh"]},
    },
    ("ccee", "pld-horario-submercado"): {
        "id": "ds-ccee-pld",
        "code": "pld_horario_submercado",
        "name": "PLD horario por submercado",
        "domain": "Preco de liquidacao das diferencas",
        "description": "Serie publica do preco de liquidacao das diferencas por submercado.",
        "granularity": "hour",
        "refresh_frequency": "daily",
        "schema_summary": {"dimensions": ["submarket"], "metrics": ["pld_rs_mwh"]},
    },
}


def get_source_seeds() -> list[dict[str, str]]:
    return [
        {
            "id": source.id,
            "code": source.code,
            "name": source.name,
            "authority_type": source.authority_type,
            "refresh_strategy": source.refresh_strategy,
            "status": source.status,
        }
        for source in SOURCE_DEFINITIONS
    ]


@lru_cache(maxsize=1)
def get_dataset_seeds() -> list[CatalogDatasetSeed]:
    seeds: list[CatalogDatasetSeed] = []
    seen_titles: set[tuple[str, str]] = set()
    seen_codes: set[tuple[str, str]] = set()

    for source in SOURCE_DEFINITIONS:
        for family, title, summary, notes in _parse_inventory_tables(source.doc_path):
            normalized_title = _slugify(title)
            title_key = (source.code, normalized_title)
            if title_key in seen_titles:
                continue

            override = _DATASET_OVERRIDES.get(title_key)
            if override is not None:
                code = override["code"]
                seed = CatalogDatasetSeed(
                    id=override["id"],
                    source_id=source.id,
                    source_code=source.code,
                    code=code,
                    name=override["name"],
                    domain=override["domain"],
                    description=override["description"],
                    granularity=override["granularity"],
                    refresh_frequency=override["refresh_frequency"],
                    schema_summary=override["schema_summary"],
                )
            else:
                code = _stable_dataset_code(source.code, title)
                if (source.code, code) in seen_codes:
                    code = f"{code}-{str(uuid5(NAMESPACE_URL, f'{source.code}:{title}'))[:8]}"
                seed = CatalogDatasetSeed(
                    id=str(uuid5(NAMESPACE_URL, f"ontogrid:{source.code}:{title}")),
                    source_id=source.id,
                    source_code=source.code,
                    code=code,
                    name=title,
                    domain=family,
                    description=summary or title,
                    granularity=_infer_granularity(title, summary, notes),
                    refresh_frequency=_infer_refresh_frequency(summary, notes),
                    schema_summary={"dimensions": [], "metrics": []},
                )

            seeds.append(seed)
            seen_titles.add(title_key)
            seen_codes.add((source.code, code))

    return seeds


def expected_dataset_totals_by_source() -> dict[str, int]:
    totals: dict[str, int] = {}
    for seed in get_dataset_seeds():
        totals[seed.source_code] = totals.get(seed.source_code, 0) + 1
    return totals


def _parse_inventory_tables(path: Path) -> list[tuple[str, str, str, str]]:
    lines = _read_text(path).splitlines()
    items: list[tuple[str, str, str, str]] = []
    current_family = ""
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue

        if line.startswith("#"):
            cleaned = _clean_heading(line)
            if cleaned:
                current_family = cleaned
            index += 1
            continue

        if not line.startswith("|"):
            index += 1
            continue

        cells = _parse_markdown_row(line)
        header_kind = _inventory_header_kind(cells)
        if header_kind:
            index += 1
            while index < len(lines):
                row = lines[index].strip()
                if not row.startswith("|"):
                    break
                row_cells = _parse_markdown_row(row)
                if _is_separator_row(row_cells):
                    index += 1
                    continue

                if header_kind == "dataset_first":
                    family = current_family
                    title = _clean_cell(row_cells[0]) if row_cells else ""
                    summary = _clean_cell(row_cells[1]) if len(row_cells) > 1 else ""
                    notes = _clean_cell(row_cells[2]) if len(row_cells) > 2 else ""
                else:
                    family = _clean_cell(row_cells[0]) if row_cells else ""
                    title = _clean_cell(row_cells[1]) if len(row_cells) > 1 else ""
                    summary = _clean_cell(row_cells[2]) if len(row_cells) > 2 else ""
                    notes = _clean_cell(row_cells[3]) if len(row_cells) > 3 else ""

                if title and family:
                    items.append((family, title, summary, notes))
                index += 1
            continue

        index += 1

    return items


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text()


def _clean_heading(value: str) -> str:
    cleaned = value.lstrip("#").strip()
    cleaned = _clean_cell(cleaned)
    cleaned = re.sub(r"^\d+(?:\.\d+)*\s*", "", cleaned)
    return cleaned.strip()


def _parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    if not stripped:
        return []
    return [cell.strip() for cell in stripped.split("|")]


def _inventory_header_kind(cells: list[str]) -> str | None:
    if len(cells) < 2:
        return None
    first = _slugify(_clean_cell(cells[0]))
    second = _slugify(_clean_cell(cells[1]))
    if first in {"dataset", "conjunto-de-dados"} and second.startswith("o-que-existe"):
        return "dataset_first"
    if first in {"organizacao", "familia-analitica"} and second == "dataset":
        return "family_first"
    return None


def _is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return True
    return all(set(cell) <= {"-", ":"} for cell in cells if cell)


def _clean_cell(value: str) -> str:
    cleaned = value.replace("**", "").replace("`", "").replace("\\_", "_")
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


def _stable_dataset_code(source_code: str, title: str) -> str:
    slug = _slugify(title)
    if not slug:
        slug = str(uuid5(NAMESPACE_URL, f"{source_code}:{title}"))
    return slug[:120]


def _infer_granularity(title: str, summary: str, notes: str) -> str:
    text = _slugify(" ".join([title, summary, notes]))
    checks = (
        ("horaria", "hour"),
        ("horario", "hour"),
        ("diaria", "day"),
        ("diario", "day"),
        ("mensal", "month"),
        ("anual", "year"),
        ("semanal", "week"),
    )
    for token, granularity in checks:
        if token in text:
            return granularity
    if "cadastro" in text or "sem-historico" in text:
        return "static"
    return "varied"


def _infer_refresh_frequency(summary: str, notes: str) -> str:
    text = _slugify(" ".join([summary, notes]))
    checks = (
        ("atualizacao-diaria", "daily"),
        ("atualizacao-semanal", "weekly"),
        ("atualizacao-mensal", "monthly"),
        ("atualizacao-anual", "yearly"),
        ("sob-demanda", "on_demand"),
        ("sem-periodicidade-fixa", "on_demand"),
    )
    for token, frequency in checks:
        if token in text:
            return frequency
    return "unknown"
