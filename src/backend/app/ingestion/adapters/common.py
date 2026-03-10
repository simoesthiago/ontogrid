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
