from pydantic import BaseModel
from typing import Any


class NetworkSummary(BaseModel):
    substations: int | None = None
    transformers: int | None = None
    operational: int | None = None
    alerts: int | None = None


class NetworkAsset(BaseModel):
    _id: str | None = None
    type: str | None = None
    code: str | None = None
    description: str | None = None
    region: str | None = None
    tension: float | None = None
    status: str | None = None
    load_kw: float | None = None
    coordinates: list | None = None


class NetworkTransformerDetail(BaseModel):
    _id: str | None = None
    code: str | None = None
    distributor_code: str | None = None
    description: str | None = None
    geodatabase_id: Any | None = None
    connection_phases: str | None = None
    status: str | None = None
    unit_type: str | None = None
    position: str | None = None
    location_area: str | None = None
    configuration: str | None = None
    substation: str | None = None
    nominal_power_kva: float | None = None
    fuse_capacity: float | None = None
    switch_capacity: float | None = None
    iron_losses_kw: float | None = None
    copper_losses_kw: float | None = None
    connection_date: str | None = None
    geometry: dict | None = None


class SubstationDetail(BaseModel):
    _id: str | None = None
    code: str | None = None
    distributor_code: str | None = None
    description: str | None = None
    shape_length: float | None = None
    shape_area: float | None = None
    geodatabase_id: Any | None = None
    geometry: dict | None = None
    qtd_transformers: int | None = None
    qtd_feeders: int | None = None