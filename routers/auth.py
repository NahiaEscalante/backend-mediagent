from fastapi import APIRouter, HTTPException, status

from schemas.auth import LoginRequest, LoginResponse
from services.auth_service import crear_access_token, validar_credenciales

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    """Valida email y contraseña; devuelve access_token o 401."""
    user = validar_credenciales(body.email, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    token = crear_access_token(sub=user["id"])
    return LoginResponse(access_token=token)
