"""Configuración desde variables de entorno."""
import os
from pathlib import Path

# Ruta base del proyecto (donde está main.py)
BASE_DIR = Path(__file__).resolve().parent
BD_DIR = BASE_DIR / "bd"

_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:8080").strip()
# "*" = permitir cualquier origen; si no, lista separada por comas
CORS_ORIGINS = ["*"] if _cors_raw == "*" else [o.strip() for o in _cors_raw.split(",") if o.strip()]
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion-clave-secreta-muy-larga")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
