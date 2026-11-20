import pandas as pd
import numpy as np


def compute_anomaly_metrics(df: pd.DataFrame, window: int = 20, threshold: float = 2.5) -> pd.DataFrame:
    """حساب المتوسط المتحرك، الانحراف المعياري، نطاقات الثقة، ودرجة الشذوذ Z-Score."""
    if "Close" not in df.columns:
        raise ValueError("Missing required 'Close' column in input DataFrame.")

    data = df.copy()

    # التغير المئوي اليومي
    data["Pct_Change"] = data["Close"].pct_change() * 100

    # المتوسط المتحرك والانحراف المعياري
    data["Rolling_Mean"] = data["Close"].rolling(window=window).mean()
    data["Rolling_Std"] = data["Close"].rolling(window=window).std()

    # معادلة Z-Score الحتمية (مع تجنب القسمة على صفر)
    data["Z_Score"] = np.where(
        data["Rolling_Std"] > 0,
        (data["Close"] - data["Rolling_Mean"]) / data["Rolling_Std"],
        0.0,
    )

    # نطاقات الثقة العلوية والسفلية للرسم البياني
    data["Upper_Band"] = data["Rolling_Mean"] + (threshold * data["Rolling_Std"])
    data["Lower_Band"] = data["Rolling_Mean"] - (threshold * data["Rolling_Std"])

    # تصنيف الشذوذ الإحصائي
    data["Is_Anomaly"] = data["Z_Score"].abs() >= threshold
    return data.dropna()