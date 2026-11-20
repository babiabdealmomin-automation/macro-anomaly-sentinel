import numpy as np
import pandas as pd
import pytest

from src.analytics import compute_anomaly_metrics
from src.notifier import build_html_report
from src.subscriptions import is_valid_email


def test_compute_anomaly_metrics_detects_spike():
    dates = pd.date_range("2026-01-01", periods=25, freq="D")
    prices = [100.0] * 24 + [150.0]
    df = pd.DataFrame({"Close": prices}, index=dates)

    result = compute_anomaly_metrics(df, window=20, threshold=2.5)
    assert bool(result["Is_Anomaly"].iloc[-1]) is True
    assert result["Z_Score"].iloc[-1] > 2.5


def test_compute_anomaly_metrics_normal_regime():
    dates = pd.date_range("2026-01-01", periods=25, freq="D")
    prices = np.linspace(100.0, 102.0, 25)
    df = pd.DataFrame({"Close": prices}, index=dates)

    result = compute_anomaly_metrics(df, window=20, threshold=2.5)
    assert bool(result["Is_Anomaly"].iloc[-1]) is False


def test_build_html_report_and_email_validation():
    sample = [
        {
            "asset": "Gold Futures",
            "date": "2026-11-20",
            "close": 3581.70,
            "pct_change": -2.82,
            "z_score": -2.55,
            "is_anomaly": True,
            "brief_en": "Gold dropped sharply.",
            "brief_ar": "انخفض الذهب بشكل حاد.",
        }
    ]
    html = build_html_report(sample, "2026-11-20")
    assert "Gold Futures" in html
    assert "ANOMALY" in html
    assert is_valid_email("client@example.com") is True
    assert is_valid_email("invalid-email") is False