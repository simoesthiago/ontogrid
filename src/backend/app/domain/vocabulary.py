from __future__ import annotations


PUBLIC_ENTITY_TYPES = frozenset(
    {
        "agent",
        "plant",
        "generation_unit",
        "distributor",
        "municipality",
        "subsystem",
        "submarket",
        "reservoir",
    }
)

PUBLIC_RELATION_TYPES = frozenset(
    {
        "OPERATED_BY",
        "OWNED_BY",
        "HAS_UNIT",
        "LOCATED_IN",
        "BELONGS_TO_SUBSYSTEM",
        "MAPPED_TO_SUBMARKET",
        "HAS_TARIFF",
        "HAS_QUALITY_INDICATOR",
    }
)

SEMANTIC_VALUE_TYPES = frozenset({"observed", "accounted", "regulatory_effective"})

REFERENCE_TIME_KINDS = frozenset({"instant", "effective_date", "reference_month"})


def validate_entity_type(value: str) -> str:
    if value not in PUBLIC_ENTITY_TYPES:
        raise ValueError(f"Unsupported public entity_type: {value}")
    return value


def validate_relation_type(value: str) -> str:
    if value not in PUBLIC_RELATION_TYPES:
        raise ValueError(f"Unsupported public relation_type: {value}")
    return value


def validate_semantic_value_type(value: str) -> str:
    if value not in SEMANTIC_VALUE_TYPES:
        raise ValueError(f"Unsupported semantic_value_type: {value}")
    return value


def validate_reference_time_kind(value: str) -> str:
    if value not in REFERENCE_TIME_KINDS:
        raise ValueError(f"Unsupported reference_time_kind: {value}")
    return value
