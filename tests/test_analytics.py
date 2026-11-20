"""
Unit tests for the deterministic Z-Score anomaly detection engine.
"""

import numpy as np
import pandas as pd
import pytest

from src.analytics import compute_anomaly_metrics


def test_detects_statistical_spike_anomaly() -> None:
    """Verifies that a sudden price spike exceeding 2.5 sigma is flagged as an anomaly."""
    # 25 days of stable prices around 100.0 followed by a sharp spike to 130.0
    prices = [100.0 + (i % 2) * 0.5 for i in range(25)] + [130.0]
    df = pd.DataFrame({"Close": prices}, index=pd.date_range("2026-01-01", periods=len(prices)))

    result = compute_anomaly_metrics(df, window=20, threshold=2.5)
    latest_row = result.iloc[-1]

    assert bool(latest_row["Is_Anomaly"]) is True
    assert latest_row["Z_Score"] > 2.5


def test_normal_volatility_not_flagged() -> None:
    """Verifies that normal price fluctuations remain below the anomaly threshold."""
    rng = np.random.default_rng(seed=42)
    prices = 100.0 + rng.normal(0, 1.0, size=40)
    df = pd.DataFrame({"Close": prices}, index=pd.date_range("2026-01-01", periods=40))

    result = compute_anomaly_metrics(df, window=20, threshold=2.5)
    assert result["Is_Anomaly"].sum() == 0


def test_missing_close_column_raises_error() -> None:
    """Ensures missing required columns raise a clear ValueError."""
    df = pd.DataFrame({"Open": [10, 20, 30]})
    with pytest.raises(ValueError, match="Close"):
        compute_anomaly_metrics(df)