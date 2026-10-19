"""
Application configuration and path resolution for CircularRoute Backend.

Anchors canonical storage directories to the backend root directory so that
runtime behavior is deterministic regardless of the process's current working directory (CWD).
Supports absolute and relative environment-variable overrides via UPLOAD_DIR and OUTPUT_DIR.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Backend directory: c:/.../CircularRoute/backend
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Project root directory: c:/.../CircularRoute
PROJECT_ROOT = BACKEND_DIR.parent

# Load .env file from backend or project root if present
if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
elif (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env")
else:
    load_dotenv()


def resolve_storage_path(env_var_name: str, default_folder_name: str) -> Path:
    """
    Resolves a storage directory path:
    1. If environment variable is set and is an absolute path, use it.
    2. If environment variable is set and is a relative path, resolve it relative to BACKEND_DIR.
    3. If environment variable is not set, default to BACKEND_DIR / default_folder_name.
    Ensures the directory exists.
    """
    raw_val = os.getenv(env_var_name)
    if raw_val:
        p = Path(raw_val)
        target = p if p.is_absolute() else (BACKEND_DIR / p).resolve()
    else:
        target = (BACKEND_DIR / default_folder_name).resolve()

    target.mkdir(parents=True, exist_ok=True)
    return target


# Canonical storage directories anchored to BACKEND_DIR
UPLOAD_DIR = resolve_storage_path("UPLOAD_DIR", "uploads")
OUTPUT_DIR = resolve_storage_path("OUTPUT_DIR", "outputs")
DIAGNOSTICS_DIR = resolve_storage_path("DIAGNOSTICS_DIR", "diagnostics")
