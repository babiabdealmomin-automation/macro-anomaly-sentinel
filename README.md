# 📡 Macro-Economic & Anomaly Sentinel

![Sentinel CI](https://github.com/babiabdealmomin-automation/macro-anomaly-sentinel/actions/workflows/sentinel_ci.yml/badge.svg)
![Daily Alert Pipeline](https://github.com/babiabdealmomin-automation/macro-anomaly-sentinel/actions/workflows/daily_alert.yml/badge.svg)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)
![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E.svg)
![Gemini 2.5 Flash](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-8E75B2.svg)

An end-to-end **Multi-Tenant Financial Telemetry & Anomaly Detection SaaS** that monitors key macro-economic assets (**Gold Futures**, **WTI Crude Oil**, and **EUR/USD**), detects statistical regime shifts using deterministic Rolling Z-Scores ($|Z| \ge 2.5\sigma$), generates bilingual executive briefings (English & Arabic) via **Gemini 2.5 Flash**, and dispatches tailored daily HTML email reports to subscribed users.

---

## 🏗️ System Architecture

```text
┌───────────────────┐     ┌──────────────────────┐     ┌─────────────────────────┐
│  Yahoo Finance    │────▶│  Analytics Engine    │────▶│  Gemini 2.5 Flash       │
│  (Live Telemetry) │     │  (Rolling Z-Score)   │     │  (Bilingual Briefings)  │
└───────────────────┘     └──────────────────────┘     └─────────────────────────┘
                                     │                               │
                                     ▼                               ▼
┌───────────────────┐     ┌──────────────────────┐     ┌─────────────────────────┐
│  Streamlit Cloud  │◀───▶│  Supabase PostgreSQL │◀────│  GitHub Actions (Cron)  │
│  (Interactive UI) │     │  (Subscribers Store) │     │  (Daily SMTP Dispatch)  │
└───────────────────┘     └──────────────────────┘     └─────────────────────────┘
```

---

## ✨ Key Features

* **Deterministic Anomaly Detection (`src/analytics.py`):** Computes rolling mean ($\mu$), rolling standard deviation ($\sigma$), confidence bands ($\pm 2.5\sigma$), and Rolling Z-Score ($Z = \frac{X - \mu}{\sigma}$) purely in NumPy/Pandas to isolate statistically significant market shocks without LLM arithmetic drift.
* **Bilingual Executive AI Intelligence (`src/ai_analyst.py`):** Synthesizes verified statistical metrics and live financial news headlines into concise, institutional-grade briefings in both **English** and **Arabic** using `Gemini 2.5 Flash`.
* **Interactive Plotly Telemetry Dashboard (`app.py`):** Real-time parameter tuning (asset selection, rolling window, Z-Score threshold), dynamic volatility bands, highlighted anomaly markers, and local `SQLite` caching (`src/database.py`).
* **Multi-Tenant Client Subscriptions (`src/subscriptions.py`):** Visitors can subscribe directly from the Streamlit sidebar, choose specific financial assets to track, or unsubscribe at any time via **Supabase PostgreSQL**.
* **Automated Daily Email Pipeline (`src/daily_report.py` & `src/notifier.py`):** Scheduled GitHub Actions Cron workflow (`Mon–Fri at 22:00 UTC`) computes daily intelligence once and dispatches personalized HTML executive reports to each active subscriber via Gmail SMTP.
* **Automated CI/CD Testing (`tests/test_analytics.py`):** Continuous integration pipeline validating anomaly detection math, HTML report generation, and email validation on every push.

---

## 📂 Project Structure

```text
macro-anomaly-sentinel/
├── .github/
│   └── workflows/
│       ├── sentinel_ci.yml       # Automated Pytest CI pipeline
│       └── daily_alert.yml       # Scheduled Cron job for daily email alerts
├── src/
│   ├── fetcher.py                # Market data & financial news ingestion (yfinance)
│   ├── analytics.py              # Deterministic Rolling Z-Score computation
│   ├── ai_analyst.py             # Bilingual Gemini 2.5 Flash briefing generator
│   ├── database.py               # Local SQLite telemetry & briefing cache
│   ├── subscriptions.py          # Supabase PostgreSQL subscriber management
│   ├── notifier.py               # HTML email builder & Gmail SMTP dispatcher
│   └── daily_report.py           # CLI entrypoint for multi-tenant daily reports
├── tests/
│   └── test_analytics.py         # Unit tests for analytics, notifier, and validation
├── app.py                        # Streamlit web application & subscription UI
├── requirements.txt              # Project dependencies
└── .env.example                  # Environment variables template
```

---

## 🚀 Quick Start (Local Setup)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/babiabdealmomin-automation/macro-anomaly-sentinel.git
   cd macro-anomaly-sentinel
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your credentials:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_public_key
   SMTP_EMAIL=your_gmail@gmail.com
   SMTP_APP_PASSWORD=your_16_char_gmail_app_password
   RECIPIENT_EMAIL=fallback_recipient@gmail.com
   ```

4. **Initialize Supabase Database Table:**
   Run the following SQL in your Supabase SQL Editor:
   ```sql
   CREATE TABLE IF NOT EXISTS subscribers (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       assets TEXT[] NOT NULL DEFAULT ARRAY['GC=F', 'CL=F', 'EURUSD=X'],
       is_active BOOLEAN NOT NULL DEFAULT TRUE,
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
       updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```

5. **Run the Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```

6. **Run Automated Tests or Daily Report CLI:**
   ```bash
   python -m pytest -v
   python -m src.daily_report
   ```
   ## LINK OF DASHBOARD
https://macro-anomaly-sentinel-sjzn53dptpvutlx4pbbuek.streamlit.app/
---

## 👤 Author

**Abde Almomin Babi** — Data & AI Engineering Portfolio (`BABI.AI`)  
*GitHub:* [@babiabdealmomin-automation](https://github.com/babiabdealmomin-automation)
