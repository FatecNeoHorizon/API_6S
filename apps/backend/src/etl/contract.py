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

def build_transform_result(valid_docs, rejected_docs, total_input):
    return {
        "valid": valid_docs,
        "rejected": rejected_docs,
        "stats": {
            "total_input": int(total_input),
            "total_valid": int(len(valid_docs)),
            "total_rejected": int(len(rejected_docs))
        }
    }
