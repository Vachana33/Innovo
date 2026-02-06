from __future__ import annotations

from supabase import Client, create_client

from app.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_STORAGE_BUCKET, SUPABASE_URL


def get_supabase_client() -> Client:
    """
    Backend-only Supabase client.
    Uses SERVICE ROLE key -> never expose to frontend.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment.")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_bucket_name() -> str:
    if not SUPABASE_STORAGE_BUCKET:
        raise RuntimeError("Missing SUPABASE_STORAGE_BUCKET in environment.")
    return SUPABASE_STORAGE_BUCKET
