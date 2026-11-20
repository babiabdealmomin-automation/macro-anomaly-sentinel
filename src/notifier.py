import os
import smtplib
from email.message import EmailMessage


def build_html_report(reports: list[dict], run_date: str) -> str:
    rows_html = ""
    briefings_html = ""

    for r in reports:
        status_badge = (
            '<span style="background:#ef4444;color:#fff;padding:3px 8px;border-radius:4px;font-weight:bold;">ANOMALY</span>'
            if r["is_anomaly"]
            else '<span style="background:#10b981;color:#fff;padding:3px 8px;border-radius:4px;font-weight:bold;">NORMAL</span>'
        )
        rows_html += f"""
        <tr style="border-bottom:1px solid #1e293b;">
            <td style="padding:10px;font-weight:bold;">{r['asset']}</td>
            <td style="padding:10px;">{r['date']}</td>
            <td style="padding:10px;">{r['close']:,.4f}</td>
            <td style="padding:10px;">{r['pct_change']:+.2f}%</td>
            <td style="padding:10px;font-weight:bold;">{r['z_score']:+.2f}σ</td>
            <td style="padding:10px;">{status_badge}</td>
        </tr>
        """

        briefings_html += f"""
        <div style="background:#111827;border-left:4px solid #38bdf8;padding:12px;margin-bottom:12px;border-radius:6px;">
            <h4 style="margin:0 0 6px 0;color:#38bdf8;">{r['asset']} ({r['date']})</h4>
            <p style="margin:0 0 8px 0;color:#e2e8f0;font-size:14px;">{r['brief_en']}</p>
            <p dir="rtl" style="margin:0;color:#a7f3d0;font-size:14px;text-align:right;">{r['brief_ar']}</p>
        </div>
        """

    return f"""
    <html>
    <body style="background:#0b0f19;color:#f8fafc;font-family:Arial,sans-serif;padding:20px;">
        <div style="max-width:720px;margin:auto;background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:24px;">
            <h2 style="color:#38bdf8;margin-top:0;">📡 Macro-Economic & Anomaly Sentinel</h2>
            <p style="color:#94a3b8;">Personalized Market Telemetry Briefing — <strong>{run_date}</strong></p>

            <table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;text-align:left;">
                <thead>
                    <tr style="background:#1e293b;color:#38bdf8;">
                        <th style="padding:10px;">Asset</th>
                        <th style="padding:10px;">Date</th>
                        <th style="padding:10px;">Close</th>
                        <th style="padding:10px;">Change</th>
                        <th style="padding:10px;">Z-Score</th>
                        <th style="padding:10px;">Regime</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <h3 style="color:#f8fafc;border-bottom:1px solid #1e293b;padding-bottom:8px;">🧠 Executive AI Briefings</h3>
            {briefings_html}

            <p style="color:#64748b;font-size:12px;margin-top:24px;text-align:center;">
                Automated Intelligence Pipeline • Built by BABI.AI
            </p>
        </div>
    </body>
    </html>
    """


def send_email_report(reports: list[dict], run_date: str, recipient_email: str) -> None:
    smtp_email = os.getenv("SMTP_EMAIL", "").strip()
    smtp_password = os.getenv("SMTP_APP_PASSWORD", "").strip()

    if not smtp_email or not smtp_password or not recipient_email:
        raise ValueError("Missing SMTP_EMAIL, SMTP_APP_PASSWORD, or recipient_email.")

    anomaly_count = sum(1 for r in reports if r["is_anomaly"])
    subject_prefix = f"🚨 [{anomaly_count} ANOMALY DETECTED]" if anomaly_count > 0 else "📊 [DAILY BRIEFING]"

    msg = EmailMessage()
    msg["Subject"] = f"{subject_prefix} Macro-Economic Sentinel — {run_date}"
    msg["From"] = f"Macro Sentinel <{smtp_email}>"
    msg["To"] = recipient_email
    msg.set_content("Your email client does not support HTML. Please view this report in an HTML-enabled client.")
    msg.add_alternative(build_html_report(reports, run_date), subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_email, smtp_password)
        server.send_message(msg)