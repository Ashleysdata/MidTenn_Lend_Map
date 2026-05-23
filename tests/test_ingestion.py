"""Unit tests for ingestion helper functions (no real API calls)."""
from unittest.mock import patch, MagicMock


def make_mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    return mock


# ── FRED ──────────────────────────────────────────────────────────────────────

def test_fred_fetch_series_returns_observations():
    from src.ingestion.fred_ingestion import fetch_series

    mock = make_mock_response({
        "observations": [
            {"date": "2023-01-01", "value": "5.33"},
            {"date": "2023-02-01", "value": "5.58"},
        ]
    })
    with patch("src.ingestion.fred_ingestion.requests.get", return_value=mock):
        result = fetch_series("FEDFUNDS")

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["date"] == "2023-01-01"
    assert result[1]["value"] == "5.58"


def test_fred_fetch_series_missing_key_returns_empty():
    from src.ingestion.fred_ingestion import fetch_series

    mock = make_mock_response({})
    with patch("src.ingestion.fred_ingestion.requests.get", return_value=mock):
        result = fetch_series("FEDFUNDS")

    assert result == []


# ── FDIC ──────────────────────────────────────────────────────────────────────

def test_fdic_fetch_institutions_extracts_data():
    from src.ingestion.fdic_ingestion import fetch_institutions

    mock = make_mock_response({
        "data": [
            {"data": {"NAME": "Wilson Bank", "COUNTY": "Wilson", "ASSET": 1_000_000}},
            {"data": {"NAME": "Avenue Bank", "COUNTY": "Davidson", "ASSET": 500_000}},
        ]
    })
    with patch("src.ingestion.fdic_ingestion.requests.get", return_value=mock):
        result = fetch_institutions()

    assert len(result) == 2
    assert result[0]["NAME"] == "Wilson Bank"
    assert result[1]["COUNTY"] == "Davidson"


def test_fdic_fetch_institutions_empty_response():
    from src.ingestion.fdic_ingestion import fetch_institutions

    mock = make_mock_response({"data": []})
    with patch("src.ingestion.fdic_ingestion.requests.get", return_value=mock):
        result = fetch_institutions()

    assert result == []
