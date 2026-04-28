from __future__ import annotations

from typing import Any, TypedDict


TRANSFORM_CONTRACT_VERSION = "1.0"


class TransformRejection(TypedDict):
    row: dict[str, Any]
    reason: str


class TransformStats(TypedDict):
    total_input: int
    total_valid: int
    total_rejected: int


class TransformResult(TypedDict):
    contract_version: str
    valid: list[dict[str, Any]]
    rejected: list[TransformRejection]
    stats: TransformStats


def build_transform_result(
    valid: list[dict[str, Any]],
    rejected: list[TransformRejection],
    total_input: int,
) -> TransformResult:
    total_valid = len(valid)
    total_rejected = len(rejected)

    return {
        "contract_version": TRANSFORM_CONTRACT_VERSION,
        "valid": valid,
        "rejected": rejected,
        "stats": {
            "total_input": total_input,
            "total_valid": total_valid,
            "total_rejected": total_rejected,
        },
    }