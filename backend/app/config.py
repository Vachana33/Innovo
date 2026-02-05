import os
from dotenv import load_dotenv

load_dotenv()

def must_getenv(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

DATABASE_URL = must_getenv("DATABASE_URL")
JWT_SECRET_KEY = must_getenv("JWT_SECRET_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "innovo-files")
