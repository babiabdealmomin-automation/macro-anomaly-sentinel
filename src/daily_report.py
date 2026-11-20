from datetime import datetime, timezone
from dotenv import load_dotenv

from src.fetcher import ASSETS, fetch_market_data, fetch_asset_news
from src.analytics import compute_anomaly_metrics
from src.ai_analyst import generate_executive_briefing
from src.notifier import send_email_report
from src.subscriptions import get_active_subscribers


def run_daily_sentinel() -> None:
    load_dotenv()

    subscribers = get_active_subscribers()
    if not subscribers:
        print("No active subscribers found. Skipping email dispatch.")
        return

    reports_by_ticker = {}
    for ticker, asset_label in ASSETS.items():
        df = fetch_market_data(ticker=ticker, period="3mo")
        metrics_df = compute_anomaly_metrics(df, window=20, threshold=2.5)
        latest = metrics_df.iloc[-1]
        latest_date = metrics_df.index[-1].strftime("%Y-%m-%d")

        headlines = fetch_asset_news(ticker, limit=3)
        briefing = generate_executive_briefing(
            asset_name=asset_label,
            date_str=latest_date,
            close_price=float(latest["Close"]),
            pct_change=float(latest["Pct_Change"]),
            z_score=float(latest["Z_Score"]),
            is_anomaly=bool(latest["Is_Anomaly"]),
            headlines=headlines,
        )

        reports_by_ticker[ticker] = {
            "ticker": ticker,
            "asset": asset_label,
            "date": latest_date,
            "close": float(latest["Close"]),
            "pct_change": float(latest["Pct_Change"]),
            "z_score": float(latest["Z_Score"]),
            "is_anomaly": bool(latest["Is_Anomaly"]),
            "brief_en": briefing["en"],
            "brief_ar": briefing["ar"],
        }

    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sent_count = 0
    for sub in subscribers:
        recipient = sub.get("email")
        selected_tickers = sub.get("assets") or list(ASSETS.keys())
        custom_reports = [reports_by_ticker[t] for t in selected_tickers if t in reports_by_ticker]

        if recipient and custom_reports:
            try:
                send_email_report(reports=custom_reports, run_date=run_date, recipient_email=recipient)
                sent_count += 1
                print(f"Sent tailored report to {recipient} ({len(custom_reports)} assets)")
            except Exception as exc:
                print(f"Failed to send report to {recipient}: {exc}")

    print(f"Completed daily dispatch: {sent_count}/{len(subscribers)} emails sent.")


if __name__ == "__main__":
    run_daily_sentinel()