import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

from src.fetcher import TRACKED_ASSETS, fetch_market_data, fetch_asset_news
from src.analytics import compute_anomaly_metrics
from src.database import SentinelDatabase
from src.ai_analyst import generate_executive_briefing
from src.subscriptions import upsert_subscriber, unsubscribe_email

load_dotenv()
db = SentinelDatabase()

st.set_page_config(
    page_title="Macro-Economic & Anomaly Sentinel",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    .brief-card-en {
        background-color: #0f172a;
        border-left: 4px solid #38bdf8;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        color: #e2e8f0;
    }
    .brief-card-ar {
        background-color: #064e3b;
        border-right: 4px solid #10b981;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        color: #ecfdf5;
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar Controls & Client Subscription ---
with st.sidebar:
    st.header("⚙️ Sentinel Controls")

    selected_ticker = st.selectbox(
        "Select Financial Asset / الأصل المالي",
        options=list(TRACKED_ASSETS.keys()),
        format_func=lambda k: TRACKED_ASSETS[k],
    )

    lookback_period = st.selectbox(
        "Lookback Period / الفترة التاريخية",
        options=["3mo", "6mo", "1y", "2y"],
        index=1,
    )

    rolling_window = st.slider(
        "Rolling Window (Days) / نافذة الحساب",
        min_value=10,
        max_value=60,
        value=20,
        step=5,
    )

    z_threshold = st.slider(
        "Anomaly Z-Score Threshold / عتبة الشذوذ",
        min_value=1.5,
        max_value=4.0,
        value=2.5,
        step=0.1,
    )

    if st.button("🔄 Refresh Live Telemetry", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # --- Multi-Tenant Email Subscription Section ---
    st.divider()
    st.subheader("📬 الاشتراك في التقارير اليومية")
    with st.form("subscription_form", clear_on_submit=False):
        sub_email = st.text_input(
            "البريد الإلكتروني / Email",
            placeholder="client@example.com",
        )
        sub_assets = st.multiselect(
            "اختر الأصول للمتابعة",
            options=list(TRACKED_ASSETS.keys()),
            default=list(TRACKED_ASSETS.keys()),
            format_func=lambda k: TRACKED_ASSETS[k],
        )
        col_sub, col_unsub = st.columns(2)
        submitted = col_sub.form_submit_button("✅ اشتراك", use_container_width=True)
        unsubscribed = col_unsub.form_submit_button("🚫 إلغاء", use_container_width=True)

        if submitted:
            ok, msg = upsert_subscriber(sub_email, sub_assets)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
        elif unsubscribed:
            ok, msg = unsubscribe_email(sub_email)
            if ok:
                st.info(msg)
            else:
                st.error(msg)

# --- Main Header ---
st.title("📡 Macro-Economic & Anomaly Sentinel")
st.caption("Deterministic Rolling Z-Score Anomaly Detection & Bilingual Gemini Executive Intelligence")

@st.cache_data(ttl=900)
def load_and_compute(ticker: str, period: str, window: int, threshold: float):
    raw_df = fetch_market_data(ticker=ticker, period=period)
    return compute_anomaly_metrics(raw_df, window=window, threshold=threshold)

try:
    df_metrics = load_and_compute(selected_ticker, lookback_period, rolling_window, z_threshold)
    db.upsert_telemetry(selected_ticker, df_metrics)
except Exception as e:
    st.error(f"Telemetry Pipeline Error: {e}")
    st.stop()

latest_row = df_metrics.iloc[-1]
latest_date_str = df_metrics.index[-1].strftime("%Y-%m-%d")
latest_close = float(latest_row["Close"])
latest_pct = float(latest_row["Pct_Change"])
latest_mean = float(latest_row["Rolling_Mean"])
latest_z = float(latest_row["Z_Score"])
is_latest_anomaly = bool(latest_row["Is_Anomaly"])
anomaly_days_count = int(df_metrics["Is_Anomaly"].sum())

# --- Top KPI Row ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Latest Close Price", f"{latest_close:,.4f}", f"{latest_pct:+.2f}%")
with kpi2:
    st.metric(f"{rolling_window}-Day Rolling Mean", f"{latest_mean:,.4f}")
with kpi3:
    regime_label = "Anomaly Detected" if is_latest_anomaly else "Normal Regime"
    st.metric(
        "Current Rolling Z-Score",
        f"{latest_z:+.2f} σ",
        regime_label,
        delta_color="inverse" if is_latest_anomaly else "normal",
    )
with kpi4:
    st.metric(f"Anomalies ({lookback_period})", f"{anomaly_days_count} Days")

# --- Interactive Plotly Telemetry Chart ---
asset_name = TRACKED_ASSETS[selected_ticker]
upper_band = df_metrics["Rolling_Mean"] + (z_threshold * df_metrics["Rolling_Std"])
lower_band = df_metrics["Rolling_Mean"] - (z_threshold * df_metrics["Rolling_Std"])
anomalies_df = df_metrics[df_metrics["Is_Anomaly"]]

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df_metrics.index.tolist() + df_metrics.index.tolist()[::-1],
        y=upper_band.tolist() + lower_band.tolist()[::-1],
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name=f"Normal Volatility Band (±{z_threshold}σ)",
    )
)
fig.add_trace(
    go.Scatter(
        x=df_metrics.index,
        y=df_metrics["Rolling_Mean"],
        mode="lines",
        line=dict(color="#94a3b8", width=1.5, dash="dot"),
        name="Rolling Mean (μ)",
    )
)
fig.add_trace(
    go.Scatter(
        x=df_metrics.index,
        y=df_metrics["Close"],
        mode="lines",
        line=dict(color="#38bdf8", width=2.2),
        name="Close Price",
    )
)
fig.add_trace(
    go.Scatter(
        x=anomalies_df.index,
        y=anomalies_df["Close"],
        mode="markers",
        marker=dict(color="#ef4444", size=9, symbol="diamond", line=dict(color="#ffffff", width=1)),
        name="Statistical Anomaly (|Z| ≥ Threshold)",
    )
)

fig.update_layout(
    title=f"{asset_name} — Price Trajectory & Statistical Anomaly Bands",
    template="plotly_dark",
    height=440,
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="",
    yaxis_title="Price",
)
st.plotly_chart(fig, use_container_width=True)

# --- Bilingual AI Executive Briefing ---
st.subheader("🧠 Bilingual AI Executive Briefing / المذكرة التنفيذية الذكية")
force_refresh_ai = st.button("✨ إنشاء / تحديث موجز تنفيذي لـ Gemini")

briefing_data = None if force_refresh_ai else db.get_cached_briefing(selected_ticker, latest_date_str)
if briefing_data is None:
    with st.spinner("Generating Gemini 2.5 Flash executive briefing..."):
        headlines = fetch_asset_news(selected_ticker, limit=3)
        briefing_data = generate_executive_briefing(
            asset_name=asset_name,
            date_str=latest_date_str,
            close_price=latest_close,
            pct_change=latest_pct,
            z_score=latest_z,
            is_anomaly=is_latest_anomaly,
            headlines=headlines,
        )
        db.save_briefing(selected_ticker, latest_date_str, briefing_data["en"], briefing_data["ar"])

col_en, col_ar = st.columns(2)
with col_en:
    st.markdown(
        f"""
        <div class="brief-card-en">
            <strong>🇬🇧 English Executive Brief ({latest_date_str})</strong><br><br>
            {briefing_data['en']}
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_ar:
    st.markdown(
        f"""
        <div class="brief-card-ar">
            <strong>🇸🇦 المذكرة التنفيذية بالعربية ({latest_date_str})</strong><br><br>
            {briefing_data['ar']}
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Historical Anomalies Audit Table ---
st.divider()
with st.expander("🗄️ سجل الشذوذ التاريخي (SQLite Telemetry Audit Log)", expanded=False):
    history_df = db.get_anomalies_history(selected_ticker)
    if not history_df.empty:
        st.dataframe(
            history_df.style.format(
                {
                    "Close": "{:.4f}",
                    "Pct_Change": "{:+.4f}",
                    "Rolling_Mean": "{:.4f}",
                    "Rolling_Std": "{:.4f}",
                    "Z_Score": "{:+.4f}",
                }
            ),
            use_container_width=True,
        )
    else:
        st.info("لا توجد حالات شذوذ مسجلة لهذا الأصل حتى الآن.")
