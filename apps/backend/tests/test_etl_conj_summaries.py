import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd

from src.etl.load.load_annual_summaries import compute_annual_summaries
from src.etl.transform.transform_gdb import transform_gdb

load_decfec_module = importlib.import_module("src.etl.load.load_decfec")
load_limits_module = importlib.import_module("src.etl.load.load_limits")


class FakeConjCollection:
    def __init__(self, docs):
        self.docs = docs
        self.bulk_write_calls = []

    def find(self, *args, **kwargs):
        return list(self.docs)

    def bulk_write(self, operations, ordered=False):
        self.bulk_write_calls.append((operations, ordered))

        modified_count = 0
        for operation in operations:
            filter_doc = operation._filter
            update_doc = operation._doc
            for doc in self.docs:
                if doc.get("code") != filter_doc.get("code"):
                    continue

                for summary in doc.get("annual_summaries") or []:
                    if (
                        summary.get("indicator_type_code") == filter_doc.get("annual_summaries.indicator_type_code")
                        and summary.get("year") == filter_doc.get("annual_summaries.year")
                    ):
                        for path, value in (update_doc.get("$set") or {}).items():
                            summary[path.replace("annual_summaries.$.", "")] = value
                        modified_count += 1

        return SimpleNamespace(modified_count=modified_count)


def test_transform_gdb_maps_shape_fields_for_conj_layer():
    df = pd.DataFrame(
        [
            {
                "NOM": " Conj Norte ",
                "COD_ID": "12345",
                "Shape_Length": "12,5",
                "Shape_Area": "45.75",
                "geometry_geojson": {"type": "Polygon", "coordinates": []},
            }
        ]
    )

    result = transform_gdb(df, "CONJ", "0123456789abcdef01234567")

    assert len(result["valid"]) == 1
    document = result["valid"][0]
    assert document["shape_length"] == 12.5
    assert document["shape_area"] == 45.75
    assert document["name"] == "Conj Norte"
    assert document["code"] == "12345"


def test_transform_gdb_rejects_conj_rows_missing_identifier():
    df = pd.DataFrame(
        [
            {
                "NOM": "Conj Sem Codigo",
                "COD_ID": None,
                "Shape_Length": 10,
                "Shape_Area": 20,
                "geometry_geojson": {"type": "Polygon", "coordinates": []},
            }
        ]
    )

    result = transform_gdb(df, "CONJ", "0123456789abcdef01234567")

    assert result["valid"] == []
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["reason"] == "Missing NOM or COD_ID in CONJ"


def test_compute_annual_summaries_updates_embedded_metrics():
    conj_collection = FakeConjCollection(
        [
            {
                "code": "12345",
                "distribution_indices": [
                    {"indicator_type_code": "DEC", "year": 2024, "period": 1, "value": 2},
                    {"indicator_type_code": "DEC", "year": 2024, "period": 2, "value": 2},
                    {"indicator_type_code": "DEC", "year": 2024, "period": 3, "value": 2},
                    {"indicator_type_code": "DEC", "year": 2024, "period": 4, "value": 2},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 1, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 2, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 3, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 4, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 5, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 6, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 7, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 8, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 9, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 10, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 11, "value": 1},
                    {"indicator_type_code": "FEC", "year": 2024, "period": 12, "value": 1},
                    {"indicator_type_code": "DEC", "year": 2025, "period": 1, "value": 1},
                    {"indicator_type_code": "DEC", "year": 2025, "period": 2, "value": 1},
                    {"indicator_type_code": "DEC", "year": 2025, "period": 3, "value": 1},
                    {"indicator_type_code": "DEC", "year": 2025, "period": 4, "value": 1},
                    {"indicator_type_code": "DEC", "year": 2025, "period": 5, "value": 1},
                    {"indicator_type_code": "DEC", "year": 2025, "period": 6, "value": 1},
                ],
                "annual_summaries": [
                    {"indicator_type_code": "DEC", "year": 2024, "limit": 10.0},
                    {"indicator_type_code": "FEC", "year": 2024, "limit": 10.0},
                    {"indicator_type_code": "DEC", "year": 2025, "limit": 4.0},
                ],
            }
        ]
    )

    result = compute_annual_summaries(conj_collection)

    assert result["updated_summaries"] == 3
    assert len(conj_collection.bulk_write_calls) == 1

    summaries = conj_collection.docs[0]["annual_summaries"]
    dec_2024 = next(summary for summary in summaries if summary["indicator_type_code"] == "DEC" and summary["year"] == 2024)
    fec_2024 = next(summary for summary in summaries if summary["indicator_type_code"] == "FEC" and summary["year"] == 2024)
    dec_2025 = next(summary for summary in summaries if summary["indicator_type_code"] == "DEC" and summary["year"] == 2025)

    assert dec_2024["accumulated_value"] == 8.0
    assert dec_2024["periods_count"] == 4
    assert dec_2024["status"] == "partial"
    assert dec_2024["criticality"] == "normal"

    assert fec_2024["accumulated_value"] == 12.0
    assert fec_2024["periods_count"] == 12
    assert fec_2024["status"] == "complete"
    assert fec_2024["criticality"] == "critical"

    assert dec_2025["accumulated_value"] == 6.0
    assert dec_2025["periods_count"] == 6
    assert dec_2025["status"] == "partial"
    assert dec_2025["criticality"] == "critical"


def test_load_decfec_triggers_annual_summary_recompute(monkeypatch):
    monkeypatch.setattr(load_decfec_module, "bulk_persist", lambda *args, **kwargs: {"inserted": 1, "updated": 0, "matched": 0, "rejected": 0})
    compute_mock = MagicMock(return_value={"updated_documents": 0, "updated_summaries": 0})
    monkeypatch.setattr(load_decfec_module, "compute_annual_summaries", compute_mock)

    conj_collection = MagicMock()
    conj_collection.bulk_write.return_value = SimpleNamespace(matched_count=1, modified_count=1)

    load_decfec_module.load_decfec(
        {
            "valid": [
                {
                    "consumer_unit_set_id": "12345",
                    "indicator_type_code": "DEC",
                    "year": 2024,
                    "period": 1,
                    "value": 1.2,
                }
            ]
        },
        MagicMock(),
        conj_collection,
    )

    compute_mock.assert_called_once_with(conj_collection)


def test_load_limits_triggers_annual_summary_recompute(monkeypatch):
    compute_mock = MagicMock(return_value={"updated_documents": 0, "updated_summaries": 0})
    monkeypatch.setattr(load_limits_module, "compute_annual_summaries", compute_mock)

    conj_collection = MagicMock()
    conj_collection.bulk_write.return_value = SimpleNamespace(matched_count=1, modified_count=1)

    load_limits_module.load_limits(
        {
            "valid": [
                {
                    "code": "12345",
                    "indicator_type_code": "DEC",
                    "year": 2024,
                    "limit": 10.0,
                }
            ]
        },
        conj_collection,
    )

    compute_mock.assert_called_once_with(conj_collection)