import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

from src.fetcher import ASSETS, fetch_market_data, fetch_asset_news
from src.analytics import compute_anomaly_metrics
from src.database import init_db, save_telemetry, get_cached_briefing, save_briefing
from src.ai_analyst import generate_executive_briefing

# تحميل متغيرات البيئة (GEMINI_API_KEY)
load_dotenv()

# تهيئة قاعدة بيانات SQLite
init_db()

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="Macro-Economic & Anomaly Sentinel",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=900, show_spinner=False)
def load_and_process_asset(ticker: str, period: str, window: int, threshold: float) -> pd.DataFrame:
    """جلب البيانات وحساب المؤشرات الإحصائية مع التخزين المؤقت لمدة 15 دقيقة."""
    raw_df = fetch_market_data(ticker=ticker, period=period)
    processed_df = compute_anomaly_metrics(raw_df, window=window, threshold=threshold)
    save_telemetry(ticker=ticker, df=processed_df)
    return processed_df


def build_price_anomaly_chart(df: pd.DataFrame, asset_label: str, threshold: float) -> go.Figure:
    """بناء رسم بياني تفاعلي يوضح مسار السعر ونطاق الثقة ونقاط الشذوذ."""
    fig = go.Figure()

    # 1. نطاق الثقة العلوي والسفلي (Normal Volatility Band)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Upper_Band"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Lower_Band"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(56, 189, 248, 0.12)",
            name=f"Normal Volatility Band (±{threshold}σ)",
        )
    )

    # 2. المتوسط المتحرك
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Rolling_Mean"],
            mode="lines",
            line=dict(color="rgba(148, 163, 184, 0.8)", width=1.5, dash="dot"),
            name="Rolling Mean (μ)",
        )
    )

    # 3. منحنى سعر الإغلاق
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            line=dict(color="#38bdf8", width=2.2),
            name="Close Price",
        )
    )

    # 4. نقاط الشذوذ الإحصائي باللون الأحمر
    anomalies = df[df["Is_Anomaly"]]
    if not anomalies.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies.index,
                y=anomalies["Close"],
                mode="markers",
                marker=dict(
                    color="#ef4444",
                    size=10,
                    symbol="diamond",
                    line=dict(color="#ffffff", width=1.2),
                ),
                name="Statistical Anomaly (|Z| ≥ Threshold)",
                customdata=anomalies[["Z_Score", "Pct_Change"]],
                hovertemplate=(
                    "<b>Date:</b> %{x|%Y-%m-%d}<br>"
                    "<b>Close:</b> %{y:.4f}<br>"
                    "<b>Z-Score:</b> %{customdata[0]:.2f}σ<br>"
                    "<b>Daily Change:</b> %{customdata[1]:.2f}%<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=f"{asset_label} — Price Trajectory & Statistical Anomaly Bands",
        template="plotly_dark",
        height=440,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def main() -> None:
    # الشريط الجانبي للتحكم
    with st.sidebar:
        st.header("⚙️ Sentinel Controls")
        ticker = st.selectbox(
            "Select Financial Asset / الأصل المالي",
            options=list(ASSETS.keys()),
            format_func=lambda k: ASSETS[k],
        )
        period = st.selectbox(
            "Lookback Period / الفترة التاريخية",
            options=["3mo", "6mo", "1y"],
            index=1,
        )
        window = st.slider(
            "Rolling Window (Days) / نافذة الحساب",
            min_value=10,
            max_value=50,
            value=20,
            step=1,
        )
        threshold = st.slider(
            "Anomaly Z-Score Threshold / عتبة الشذوذ",
            min_value=1.5,
            max_value=3.5,
            value=2.5,
            step=0.1,
        )

        st.divider()
        if st.button("🔄 Refresh Live Telemetry", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # العنوان الرئيسي
    st.title("📡 Macro-Economic & Anomaly Sentinel")
    st.caption("Deterministic Rolling Z-Score Anomaly Detection & Bilingual Gemini Executive Intelligence")

    # تحميل البيانات ومعالجتها
    try:
        with st.spinner("Fetching market telemetry & computing statistical bands..."):
            df = load_and_process_asset(ticker, period, window, threshold)
    except Exception as exc:
        st.error(f"Error loading telemetry for {ticker}: {exc}")
        return

    latest_row = df.iloc[-1]
    latest_date = df.index[-1].strftime("%Y-%m-%d")
    anomaly_count = int(df["Is_Anomaly"].sum())

    # صف مؤشرات الأداء الرئيسية (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label="Latest Close Price",
        value=f"{latest_row['Close']:,.4f}",
        delta=f"{latest_row['Pct_Change']:+.2f}%",
    )
    col2.metric(
        label=f"{window}-Day Rolling Mean",
        value=f"{latest_row['Rolling_Mean']:,.4f}",
    )
    col3.metric(
        label="Current Rolling Z-Score",
        value=f"{latest_row['Z_Score']:+.2f} σ",
        delta="ANOMALY DETECTED" if latest_row["Is_Anomaly"] else "Normal Regime",
        delta_color="inverse" if latest_row["Is_Anomaly"] else "normal",
    )
    col4.metric(
        label=f"Anomalies ({period})",
        value=f"{anomaly_count} Days",
    )

    # الرسم البياني التفاعلي
    st.plotly_chart(build_price_anomaly_chart(df, ASSETS[ticker], threshold), use_container_width=True)

    # قسم المذكرة التنفيذية للذكاء الاصطناعي
    st.subheader("🧠 Bilingual AI Executive Briefing / المذكرة التنفيذية الذكية")
    force_regen = st.button("✨ Generate / Refresh Gemini Executive Brief")

    briefing = None if force_regen else get_cached_briefing(ticker, latest_date)
    if briefing is None:
        with st.spinner("Synthesizing market news & statistical signals with Gemini..."):
            headlines = fetch_asset_news(ticker, limit=3)
            briefing = generate_executive_briefing(
                asset_name=ASSETS[ticker],
                date_str=latest_date,
                close_price=float(latest_row["Close"]),
                pct_change=float(latest_row["Pct_Change"]),
                z_score=float(latest_row["Z_Score"]),
                is_anomaly=bool(latest_row["Is_Anomaly"]),
                headlines=headlines,
            )
            save_briefing(
                ticker=ticker,
                date_str=latest_date,
                z_score=float(latest_row["Z_Score"]),
                brief_en=briefing["en"],
                brief_ar=briefing["ar"],
            )

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.info(f"**🇬🇧 English Executive Brief ({latest_date})**\n\n{briefing['en']}")
    with b_col2:
        st.success(f"**🇸🇦 المذكرة التنفيذية ({latest_date})**\n\n{briefing['ar']}")

    # جدول السجل التاريخي لحالات الشذوذ (بدون الاعتماد على jinja2)
    with st.expander("📋 Historical Anomaly Log (SQLite Telemetry)", expanded=True):
        anomaly_rows = df[df["Is_Anomaly"]][["Close", "Pct_Change", "Rolling_Mean", "Rolling_Std", "Z_Score"]]
        if anomaly_rows.empty:
            st.write("No statistical anomalies detected within the selected lookback window and threshold.")
        else:
            st.dataframe(anomaly_rows.round(4), use_container_width=True)


if __name__ == "__main__":
    main()