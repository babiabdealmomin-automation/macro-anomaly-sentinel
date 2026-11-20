import yfinance as yf
import pandas as pd

ASSETS = {
    "GC=F": "Gold Futures (الذهب)",
    "CL=F": "Crude Oil WTI (النفط الخام)",
    "EURUSD=X": "EUR/USD Exchange Rate (اليورو/الدولار)",
}


def fetch_market_data(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """جلب السلسلة الزمنية اليومية للأصل المالي من Yahoo Finance."""
    asset = yf.Ticker(ticker)
    df = asset.history(period=period, interval="1d")
    if df.empty:
        raise ValueError(f"لم يتم العثور على بيانات للرمز: {ticker}")

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df


def fetch_asset_news(ticker: str, limit: int = 3) -> list[str]:
    """جلب أحدث العناوين الإخبارية المرتبطة بالأصل لتفسير الشذوذ."""
    asset = yf.Ticker(ticker)
    news_items = asset.news or []
    headlines = []
    for item in news_items[:limit]:
        content = item.get("content", {})
        title = content.get("title") or item.get("title")
        if title:
            headlines.append(title)
    return headlines