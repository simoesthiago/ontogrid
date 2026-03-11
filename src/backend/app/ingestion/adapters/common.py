from __future__ import annotations

import re
import unicodedata


_SUBMARKET_ALIASES = {
    "sudeste/centro-oeste": ("SE-CO", "Sudeste/Centro-Oeste"),
    "sudeste-centro-oeste": ("SE-CO", "Sudeste/Centro-Oeste"),
    "sudeste centro oeste": ("SE-CO", "Sudeste/Centro-Oeste"),
    "sul": ("S", "Sul"),
    "nordeste": ("NE", "Nordeste"),
    "norte": ("N", "Norte"),
}


def normalize_token(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


def normalize_lookup(value: str) -> str:
    return normalize_token(value).replace("-", " ")


def canonical_submarket(value: str) -> tuple[str, str]:
    normalized = normalize_lookup(value)
    code, name = _SUBMARKET_ALIASES.get(normalized, (normalize_token(value).upper(), value.strip()))
    return code, name


def distributor_code(name: str) -> str:
    return f"DIST-{normalize_token(name).upper()}"


def agent_code(name: str, tax_id: str | None = None) -> str:
    if tax_id:
        normalized_tax_id = re.sub(r"[^0-9]", "", tax_id)
        if normalized_tax_id:
            return f"AGENT-{normalized_tax_id}"
    return f"AGENT-{normalize_token(name).upper()}"


def plant_code(name: str, *, ceg: str | None = None, ons_plant_code: str | None = None) -> str:
    if ceg:
        normalized_ceg = normalize_token(ceg).upper()
        if normalized_ceg:
            return f"PLANT-{normalized_ceg}"
    if ons_plant_code:
        normalized_ons_code = normalize_token(ons_plant_code).upper()
        if normalized_ons_code:
            return f"PLANT-ONS-{normalized_ons_code}"
    return f"PLANT-{normalize_token(name).upper()}"


def municipality_code(name: str, ibge_code: str | None = None) -> str:
    if ibge_code:
        normalized_ibge = re.sub(r"[^0-9]", "", ibge_code)
        if normalized_ibge:
            return f"MUN-{normalized_ibge}"
    return f"MUN-{normalize_token(name).upper()}"


def subsystem_code(name: str) -> str:
    normalized = normalize_lookup(name)
    aliases = {
        "sudeste centro oeste": "SE-CO",
        "sudeste centro-oeste": "SE-CO",
        "sudeste/centro-oeste": "SE-CO",
        "sul": "S",
        "nordeste": "NE",
        "norte": "N",
    }
    return aliases.get(normalized, normalize_token(name).upper())
