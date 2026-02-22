"""Capa de acceso a datos: lectura de los JSON en bd/."""
import json
from pathlib import Path

from config import BD_DIR


def _load_json(filename: str) -> list | dict:
    """Carga un JSON desde bd/. Devuelve lista o dict vacío si no existe o es inválido."""
    path = BD_DIR / filename
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else data
    except (json.JSONDecodeError, TypeError):
        return []


def get_paciente_por_correo(correo: str) -> dict | None:
    """Devuelve el paciente con el correo dado o None."""
    pacientes = _load_json("pacientes.json")
    if not isinstance(pacientes, list):
        return None
    correo_lower = correo.strip().lower()
    for p in pacientes:
        if isinstance(p, dict) and (p.get("correo") or "").strip().lower() == correo_lower:
            return p
    return None


def get_paciente_por_id(paciente_id: str) -> dict | None:
    """Devuelve el paciente con el id dado o None."""
    pacientes = _load_json("pacientes.json")
    if not isinstance(pacientes, list):
        return None
    for p in pacientes:
        if isinstance(p, dict) and p.get("id") == paciente_id:
            return p
    return None


def get_doctores() -> list[dict]:
    """Devuelve la lista de doctores (para uso futuro del agente u otros módulos)."""
    data = _load_json("doctores.json")
    return data if isinstance(data, list) else []


def get_especialidades() -> list[dict]:
    """Devuelve la lista de especialidades."""
    data = _load_json("especialidades.json")
    return data if isinstance(data, list) else []


def get_sedes() -> list[dict]:
    """Devuelve la lista de sedes."""
    data = _load_json("sedes.json")
    return data if isinstance(data, list) else []


def get_sede_especialidades() -> list[dict]:
    """Devuelve la relación sede-especialidad."""
    data = _load_json("sede_especialidades.json")
    return data if isinstance(data, list) else []


def get_horarios() -> list[dict]:
    """Devuelve la lista de horarios."""
    data = _load_json("horarios.json")
    return data if isinstance(data, list) else []
