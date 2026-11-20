import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/sentinel.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """إنشاء جداول قاعدة بيانات SQLite إذا لم تكن موجودة."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                close_price REAL NOT NULL,
                pct_change REAL NOT NULL,
                rolling_mean REAL NOT NULL,
                rolling_std REAL NOT NULL,
                z_score REAL NOT NULL,
                is_anomaly INTEGER NOT NULL,
                UNIQUE(ticker, date)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_briefings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                z_score REAL NOT NULL,
                brief_ar TEXT NOT NULL,
                brief_en TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, date)
            )
        """)
        conn.commit()


def save_telemetry(ticker: str, df: pd.DataFrame) -> None:
    """حفظ السلاسل الزمنية والقياسات الإحصائية في SQLite مع تجنب التكرار."""
    records = [
        (
            ticker,
            idx.strftime("%Y-%m-%d"),
            float(row["Close"]),
            float(row["Pct_Change"]),
            float(row["Rolling_Mean"]),
            float(row["Rolling_Std"]),
            float(row["Z_Score"]),
            int(row["Is_Anomaly"]),
        )
        for idx, row in df.iterrows()
    ]
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO market_telemetry
            (ticker, date, close_price, pct_change, rolling_mean, rolling_std, z_score, is_anomaly)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()


def get_cached_briefing(ticker: str, date_str: str) -> dict[str, str] | None:
    """استرجاع المذكرة التنفيذية المحفوظة مسبقاً لتقليل استهلاك API."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT brief_en, brief_ar FROM ai_briefings WHERE ticker = ? AND date = ?",
            (ticker, date_str),
        ).fetchone()
    if row:
        return {"en": row[0], "ar": row[1]}
    return None


def save_briefing(ticker: str, date_str: str, z_score: float, brief_en: str, brief_ar: str) -> None:
    """حفظ المذكرة التنفيذية المولدة في قاعدة البيانات."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO ai_briefings (ticker, date, z_score, brief_en, brief_ar)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticker, date_str, z_score, brief_en, brief_ar),
        )
        conn.commit()