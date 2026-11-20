import os
import json
from google import genai


def generate_executive_briefing(
    asset_name: str,
    date_str: str,
    close_price: float,
    pct_change: float,
    z_score: float,
    is_anomaly: bool,
    headlines: list[str],
) -> dict[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    status_en = "a statistically significant anomaly" if is_anomaly else "normal market volatility"
    status_ar = "شذوذاً إحصائياً ملحوظاً" if is_anomaly else "تقلباً طبيعياً في السوق"

    fallback = {
        "en": (
            f"On {date_str}, {asset_name} closed at {close_price:,.4f} ({pct_change:+.2f}% daily change). "
            f"The rolling Z-Score reached {z_score:+.2f}σ, indicating {status_en}."
        ),
        "ar": (
            f"بتاريخ {date_str}، أغلق أصل {asset_name} عند مستوى {close_price:,.4f} (بتغير يومي {pct_change:+.2f}%). "
            f"سجل مؤشر Z-Score قيمة {z_score:+.2f}σ، مما يعكس {status_ar}."
        ),
    }

    if not api_key or api_key.startswith("ضع_"):
        return fallback

    news_block = "\n".join(f"- {h}" for h in headlines) if headlines else "No recent headlines available."
    prompt = f"""
You are a senior quantitative financial analyst. Write a concise 2-sentence executive briefing in both English and Arabic explaining the market movement below.
Rules:
1. Do NOT invent or alter any numbers.
2. Link the movement to the headlines if relevant.
3. Return ONLY valid JSON with keys "en" and "ar".

Data:
- Asset: {asset_name}
- Date: {date_str}
- Close Price: {close_price:,.4f}
- Daily Change: {pct_change:+.2f}%
- Z-Score: {z_score:+.2f} (Anomaly: {is_anomaly})
- Recent Headlines:
{news_block}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        raw_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(raw_text)
        if "en" in parsed and "ar" in parsed:
            return {"en": parsed["en"], "ar": parsed["ar"]}
    except Exception:
        pass

    return fallback
