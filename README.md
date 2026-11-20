Macro-Economic & Anomaly SentinelAn automated financial telemetry, statistical anomaly detection, and executive intelligence dashboard built with Python, Pandas/NumPy, SQLite, Streamlit, Plotly, and Google Gemini.System OverviewFinancial and supply-chain teams suffer from alert fatigue caused by normal daily market noise. Macro-Economic & Anomaly Sentinel separates routine volatility from statistically significant market shocks using a deterministic Rolling Z-Score engine, then uses Google Gemini (with strict Pydantic schema validation) to contextualize anomalies alongside live financial headlines in both English and Arabic.Key Architectural HighlightsZero-Hallucination Statistical Engine (src/analytics.py): Computes rolling mean ($\mu$), rolling standard deviation ($\sigma$), confidence bands ($\pm 2.5\sigma$), and $Z\text{-Score} = \frac{X - \mu}{\sigma}$ deterministically in NumPy/Pandas before invoking any LLM.Idempotent SQLite Persistence (src/database.py): Stores historical telemetry and caches bilingual AI briefings (UNIQUE(ticker, date)) to eliminate redundant API calls and preserve historical audit logs.Structured Bilingual AI Synthesis (src/ai_analyst.py): Enforces a Pydantic JSON schema on Gemini responses to produce crisp, 3-sentence executive briefs in both Arabic and English with automatic deterministic fallback if API quotas are reached.Interactive BI Dashboard (app.py): Real-time parameter tuning (asset selection, rolling window, Z-Score threshold), interactive Plotly anomaly bands, and downloadable historical anomaly logs.Quickstart# 1. Clone and enter project directory
git clone https://github.com/<your-username>/macro-anomaly-sentinel.git
cd macro-anomaly-sentinel

# 2. Create virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 3. Configure environment variables
copy .env.example .env
# Add your GEMINI_API_KEY inside .env

# 4. Run unit tests
pytest -v

# 5. Launch the interactive dashboard
streamlit run app.py
