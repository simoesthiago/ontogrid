from pydantic import BaseModel


class CatalogCoverageSourceItem(BaseModel):
    source_code: str
    source_name: str
    source_document: str
    inventoried_total: int
    documented_only_total: int
    adapter_enabled_total: int
    published_total: int


class CatalogCoverageFamilyItem(BaseModel):
    source_code: str
    family: str
    inventoried_total: int
    documented_only_total: int
    adapter_enabled_total: int
    published_total: int


class CatalogCoverageResponse(BaseModel):
    inventoried_total: int
    documented_only_total: int
    adapter_enabled_total: int
    published_total: int
    sources: list[CatalogCoverageSourceItem]
    families: list[CatalogCoverageFamilyItem]
