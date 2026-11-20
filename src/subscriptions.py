import os
import re
from datetime import datetime, timezone
from supabase import create_client, Client


def _get_supabase_client() -> Client | None:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        return None
    return create_client(url, key)


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))


def upsert_subscriber(email: str, assets: list[str]) -> tuple[bool, str]:
    email_clean = email.strip().lower()
    if not is_valid_email(email_clean):
        return False, "يرجى إدخال بريد إلكتروني صحيح."
    if not assets:
        return False, "يرجى اختيار أصل مالي واحد على الأقل."

    client = _get_supabase_client()
    if not client:
        return False, "إعدادات قاعدة البيانات السحابية غير مكتملة (SUPABASE_URL / SUPABASE_KEY)."

    try:
        client.table("subscribers").upsert(
            {
                "email": email_clean,
                "assets": assets,
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="email",
        ).execute()
        return True, f"تم تفعيل الاشتراك بنجاح للبريد: {email_clean}"
    except Exception as e:
        return False, f"تعذر حفظ الاشتراك: {e}"


def unsubscribe_email(email: str) -> tuple[bool, str]:
    email_clean = email.strip().lower()
    if not is_valid_email(email_clean):
        return False, "يرجى إدخال بريد إلكتروني صحيح لإلغاء الاشتراك."

    client = _get_supabase_client()
    if not client:
        return False, "إعدادات قاعدة البيانات السحابية غير مكتملة."

    try:
        client.table("subscribers").update(
            {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}
        ).eq("email", email_clean).execute()
        return True, f"تم إيقاف التنبيهات للبريد: {email_clean}"
    except Exception as e:
        return False, f"تعذر إلغاء الاشتراك: {e}"


def get_active_subscribers() -> list[dict]:
    client = _get_supabase_client()
    if not client:
        fallback_email = os.getenv("RECIPIENT_EMAIL", "").strip()
        if fallback_email:
            return [{"email": fallback_email, "assets": ["GC=F", "CL=F", "EURUSD=X"]}]
        return []

    try:
        response = (
            client.table("subscribers")
            .select("email, assets")
            .eq("is_active", True)
            .execute()
        )
        return response.data or []
    except Exception:
        return []