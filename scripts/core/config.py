import json
import os
from pathlib import Path
from typing import Dict

DEFAULTS: Dict[str, str] = {
    "CODEX_MEM_DATA_DIR": str(Path.home() / ".codex-mem"),
    "CODEX_MEM_VECTOR_ENABLED": "true",
    "CODEX_MEM_VECTOR_PROVIDER": "chroma",
    "CODEX_MEM_VECTOR_COLLECTION": "codex-mem",
    "CODEX_MEM_VECTOR_COLLECTION_TURNS": "codex-mem-turns",
    "CODEX_MEM_VECTOR_TOP_K": "50",
    "CODEX_MEM_PYTHON_VERSION": "3.13",
    "CODEX_MEM_LOG_LEVEL": "INFO",
}


def get_data_dir() -> Path:
    return Path(os.getenv("CODEX_MEM_DATA_DIR", DEFAULTS["CODEX_MEM_DATA_DIR"]))


def get_settings_path() -> Path:
    return get_data_dir() / "settings.json"


def _apply_env_overrides(values: Dict[str, str]) -> Dict[str, str]:
    out = dict(values)
    for key in DEFAULTS:
        if os.getenv(key) is not None:
            out[key] = os.getenv(key, "")
    return out


def load_settings() -> Dict[str, str]:
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    if not settings_path.exists():
        settings = _apply_env_overrides(DEFAULTS)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        return settings

    try:
        loaded = json.loads(settings_path.read_text())
        if not isinstance(loaded, dict):
            loaded = {}
    except Exception:
        loaded = {}

    merged = dict(DEFAULTS)
    for key in DEFAULTS:
        value = loaded.get(key)
        if value is not None:
            merged[key] = str(value)

    merged = _apply_env_overrides(merged)
    return merged


def get_bool(settings: Dict[str, str], key: str) -> bool:
    return str(settings.get(key, "")).strip().lower() in {"1", "true", "yes", "on"}


def get_int(settings: Dict[str, str], key: str, fallback: int) -> int:
    try:
        return int(settings.get(key, str(fallback)))
    except Exception:
        return fallback
