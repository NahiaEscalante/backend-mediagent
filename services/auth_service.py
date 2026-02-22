"""Validación de credenciales y generación de JWT."""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from services.db import get_paciente_por_correo

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# En desarrollo: los hashes en pacientes.json son simulados. Con esta contraseña
# se acepta login para cualquier usuario que tenga "simulado" en contrasena_hash.
DEV_PASSWORD_FOR_SIMULATED_HASH = "password123"


def validar_credenciales(email: str, password: str) -> dict | None:
    """
    Valida email y contraseña contra pacientes.json.
    Devuelve el dict del paciente si es válido, None si no.
    """
    paciente = get_paciente_por_correo(email)
    if not paciente:
        return None
    stored_hash = (paciente.get("contrasena_hash") or "").strip()
    if not stored_hash:
        return None
    # Bypass para hashes de desarrollo (simulados): aceptar contraseña conocida
    if "simulado" in stored_hash.lower():
        if password == DEV_PASSWORD_FOR_SIMULATED_HASH:
            return paciente
        return None
    try:
        if pwd_context.verify(password, stored_hash):
            return paciente
    except Exception:
        pass
    return None


def crear_access_token(sub: str) -> str:
    """Crea un JWT con sub (id del paciente) y exp."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire, "iat": now}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
