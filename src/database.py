import sqlite3
from pathlib import Path
import pandas as pd


class SentinelDatabase:
    def __init__(self, db_path: str = "data/sentinel.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry (
                    ticker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    close REAL,
                    pct_change REAL,
                    rolling_mean REAL,
                    rolling_std REAL,
                    z_score REAL,
                    is_anomaly INTEGER,
                    PRIMARY KEY (ticker, date)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS briefings (
                    ticker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    brief_en TEXT,
                    brief_ar TEXT,
                    PRIMARY KEY (ticker, date)
                )
                """
            )

    def upsert_telemetry(self, ticker: str, df: pd.DataFrame) -> None:
        rows = []
        for idx, row in df.iterrows():
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)
            rows.append(
                (
                    ticker,
                    date_str,
                    float(row["Close"]),
                    float(row["Pct_Change"]) if pd.notna(row["Pct_Change"]) else 0.0,
                    float(row["Rolling_Mean"]) if pd.notna(row["Rolling_Mean"]) else 0.0,
                    float(row["Rolling_Std"]) if pd.notna(row["Rolling_Std"]) else 0.0,
                    float(row["Z_Score"]) if pd.notna(row["Z_Score"]) else 0.0,
                    int(bool(row["Is_Anomaly"])),
                )
            )
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO telemetry
                (ticker, date, close, pct_change, rolling_mean, rolling_std, z_score, is_anomaly)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def get_anomalies_history(self, ticker: str) -> pd.DataFrame:
        with self._connect() as conn:
            df = pd.read_sql_query(
                """
                SELECT date AS Date, close AS Close, pct_change AS Pct_Change,
                       rolling_mean AS Rolling_Mean, rolling_std AS Rolling_Std, z_score AS Z_Score
                FROM telemetry
                WHERE ticker = ? AND is_anomaly = 1
                ORDER BY date DESC
                """,
                conn,
                params=(ticker,),
            )
        return df

    def get_cached_briefing(self, ticker: str, date_str: str) -> dict | None:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT brief_en, brief_ar FROM briefings WHERE ticker = ? AND date = ?",
                (ticker, date_str),
            )
            row = cur.fetchone()
        if row:
            return {"en": row[0], "ar": row[1]}
        return None

    def save_briefing(self, ticker: str, date_str: str, brief_en: str, brief_ar: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO briefings (ticker, date, brief_en, brief_ar)
                VALUES (?, ?, ?, ?)
                """,
                (ticker, date_str, brief_en, brief_ar),
            )
