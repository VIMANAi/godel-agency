import json
from pathlib import Path

import pytest

from src.core.data_ingestion import AnonymizationConfig, DataIngestionPipeline


def _valid_record(**overrides):
    record = {
        "id": "rec-1",
        "source": "instagram",
        "text": "Mensaje de prueba válido",
        "date": "2026-06-01T00:00:00Z",
    }
    record.update(overrides)
    return record


def test_load_raw_data_jsonl_skips_blank_and_invalid_lines(tmp_path: Path):
    pipeline = DataIngestionPipeline(base_path=tmp_path)
    input_file = tmp_path / "data" / "raw" / "input.jsonl"
    input_file.parent.mkdir(parents=True, exist_ok=True)

    input_file.write_text(
        "\n"
        f"{json.dumps(_valid_record(id='rec-1'))}\n"
        "not-json\n"
        f"{json.dumps(_valid_record(id='rec-2'))}\n"
        "   \n",
        encoding="utf-8",
    )

    loaded = pipeline.load_raw_data(input_file)

    assert [item["id"] for item in loaded] == ["rec-1", "rec-2"]


@pytest.mark.parametrize("allow_synthetic_input", [False, True])
@pytest.mark.parametrize("synthetic_marker", ["field", "path"])
def test_process_file_synthetic_filtering_respects_config(
    tmp_path: Path, allow_synthetic_input: bool, synthetic_marker: str
):
    config = AnonymizationConfig(allow_synthetic_input=allow_synthetic_input)
    pipeline = DataIngestionPipeline(config=config, base_path=tmp_path)

    if synthetic_marker == "path":
        input_file = tmp_path / "data" / "raw" / "synthetic" / "records.jsonl"
        record = _valid_record()
    else:
        input_file = tmp_path / "data" / "raw" / "records.jsonl"
        record = _valid_record(is_synthetic=True)

    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(f"{json.dumps(record)}\n", encoding="utf-8")

    result = pipeline.process_file(input_file)

    expected_valid = 1 if allow_synthetic_input else 0
    expected_invalid = 0 if allow_synthetic_input else 1
    assert result["valid_records"] == expected_valid
    assert result["invalid_records"] == expected_invalid
