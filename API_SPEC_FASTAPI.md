# Guía de implementación del backend — FastAPI (MediAgent / aura-chat)

Esta guía indica cómo implementar el backend en FastAPI para que el frontend aura-chat funcione correctamente. Sigue los pasos en orden; al final tendrás los dos endpoints que el frontend consume.

---

## Requisitos previos

- Python 3.10+
- FastAPI y uvicorn instalados (p. ej. `pip install fastapi uvicorn python-jose passlib python-multipart`)
- El frontend espera el backend en **`http://localhost:8000`** por defecto (configurable con `VITE_API_BASE_URL`)

---

## Paso 1 — Proyecto y configuración base

### 1.1 Estructura mínima sugerida

```
backend/
  main.py          # app FastAPI, CORS, rutas
  config.py       # variables de entorno (opcional)
  routers/
    auth.py        # login
    agent.py       # chat
  schemas/
    auth.py        # LoginRequest, LoginResponse
    chat.py        # ChatRequest, ChatResponse
```

### 1.2 Variables de entorno

Crea un `.env` (y un `.env.example` sin valores sensibles) con al menos:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `CORS_ORIGINS` | Orígenes permitidos (coma-separados) | `http://localhost:8080` |
| `SECRET_KEY` | Clave para firmar JWT | string largo y aleatorio |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validez del token en minutos | `60` |

El frontend en desarrollo corre en `http://localhost:8080`; ese origen debe estar en CORS.

### 1.3 CORS en FastAPI

En `main.py`, registra el middleware CORS **antes** de incluir los routers:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)
```

Sin esto, el navegador bloqueará las peticiones desde el frontend.

---

## Paso 2 — Autenticación (login)

### 2.1 Objetivo

Implementar **`POST /auth/login`**: el frontend envía email y contraseña y espera un token que guardará y enviará en el header `Authorization: Bearer <token>`.

### 2.2 Contrato del endpoint

| Aspecto | Detalle |
|---------|---------|
| **Ruta** | `POST /auth/login` |
| **Autenticación** | No (es público) |
| **Request body** | JSON con `email` (string) y `password` (string) |
| **Response 200** | JSON con `access_token` (string) |
| **Errores** | 401 si credenciales incorrectas; 422 si body inválido |

El frontend solo usa `data.access_token`; no espera otros campos en la respuesta.

### 2.3 Modelos Pydantic

Crea `schemas/auth.py` (o equivalente):

```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
```

### 2.4 Implementación del endpoint

En `routers/auth.py` (y registra el router en `main.py` bajo el prefijo que quieras, p. ej. sin prefijo):

1. Recibir el body con `LoginRequest`.
2. Validar usuario y contraseña (BD, etc.). Si falla → `HTTPException(401, detail="Credenciales inválidas")`.
3. Crear un JWT (o token opaco) con la duración configurada.
4. Devolver `LoginResponse(access_token=token)`.

Ejemplo de firma del endpoint:

```python
from fastapi import APIRouter, HTTPException, Depends
from your_app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    # 1. Validar credenciales (ej. contra BD)
    # 2. Si no válido: raise HTTPException(status_code=401, detail="Credenciales inválidas")
    # 3. token = crear_jwt(sub=user_id, expire_minutes=...)
    # 4. return LoginResponse(access_token=token)
    ...
```

Asegúrate de que la respuesta tenga exactamente el campo **`access_token`** en snake_case.

### 2.5 Respuestas de error

- **401**: credenciales incorrectas. Body sugerido: `{ "detail": "Credenciales inválidas" }`.
- **422**: FastAPI la devuelve automáticamente si el body no cumple `LoginRequest` (falta email/password o tipo incorrecto).

---

## Paso 3 — Dependencia de autenticación (Bearer token)

### 3.1 Objetivo

Crear una dependencia que lea el header `Authorization: Bearer <token>`, valide el token y opcionalmente devuelva el usuario. Las rutas protegidas (como el chat) la usarán.

### 3.2 Comportamiento

- Si no hay header o el token es inválido/expirado → lanzar `HTTPException(401, detail="No autenticado o token inválido")`.
- Si es válido → continuar (y opcionalmente inyectar el usuario en el endpoint).

Ejemplo de esqueleto:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="No autenticado o token inválido")
    token = credentials.credentials
    # Validar JWT, extraer user_id, etc. Si falla:
    # raise HTTPException(status_code=401, detail="No autenticado o token inválido")
    return user_or_payload
```

El frontend envía siempre `Authorization: Bearer <access_token>` en las peticiones que requieren auth; no envía este header en `/auth/login`.

---

## Paso 4 — Chat (agente)

### 4.1 Objetivo

Implementar **`POST /agent/chat`**: el usuario envía un mensaje (y opcionalmente un `conversation_id`); el backend devuelve la respuesta del agente y si requiere revisión humana.

### 4.2 Contrato del endpoint

| Aspecto | Detalle |
|---------|---------|
| **Ruta** | `POST /agent/chat` |
| **Autenticación** | Sí. Header `Authorization: Bearer <access_token>`. |
| **Request body** | JSON: `message` (string, obligatorio), `conversation_id` (string, opcional) |
| **Response 200** | JSON: `reply` (string), `requires_review` (boolean, opcional; si falta → false) |
| **Errores** | 401 si no autenticado; 422 si body inválido |

El frontend usa exactamente `data.reply` y `data.requires_review` (snake_case).

### 4.3 Modelos Pydantic

Crea `schemas/chat.py` (o equivalente):

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    requires_review: bool = False
```

### 4.4 Implementación del endpoint

En `routers/agent.py`:

1. Usar la dependencia de autenticación (Paso 3) para exigir token válido.
2. Recibir el body con `ChatRequest`.
3. (Opcional) Usar `conversation_id` para contexto o historial.
4. Generar la respuesta del agente (LLM, reglas, etc.) y decidir si `requires_review`.
5. Devolver `ChatResponse(reply=..., requires_review=...)`.

Ejemplo de firma:

```python
from fastapi import APIRouter, Depends
from your_app.schemas.chat import ChatRequest, ChatResponse
from your_app.auth_dependency import get_current_user

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user=Depends(get_current_user)):
    # 1. Opcional: cargar historial con body.conversation_id
    # 2. reply = generar_respuesta(body.message, ...)
    # 3. requires_review = decidir_si_revisar(reply, ...)
    # 4. return ChatResponse(reply=reply, requires_review=requires_review)
    ...
```

Respuesta de ejemplo que el frontend entiende:

```json
{
  "reply": "Los síntomas más comunes de la gripe son fiebre, tos y dolor de garganta.",
  "requires_review": false
}
```

Si la respuesta debe pasar por revisión humana, pon `requires_review: true`; el frontend mostrará el modal correspondiente.

### 4.5 Respuestas de error

- **401**: token ausente o inválido. La dependencia del Paso 3 debe lanzar `HTTPException(401)`.
- **422**: body inválido (p. ej. `message` faltante o no string). FastAPI lo devuelve automáticamente si no cumple `ChatRequest`.

---

## Paso 5 — Montar routers y arrancar

En `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from your_app.routers import auth, agent
import os

app = FastAPI()

# CORS (Paso 1.3)
origins = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)

# Routers
app.include_router(auth.router)
app.include_router(agent.router)

# Opcional: health check
@app.get("/health")
def health():
    return {"status": "ok"}
```

Arranca con:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El frontend por defecto apunta a `http://localhost:8000`; con esto debería poder llamar a login y chat.

---

## Resumen rápido (contratos exactos)

| Paso | Endpoint | Método | Request body | Response 200 |
|------|----------|--------|--------------|--------------|
| 2 | `/auth/login` | POST | `{ "email": string, "password": string }` | `{ "access_token": string }` |
| 4 | `/agent/chat` | POST | `{ "message": string, "conversation_id"?: string }` | `{ "reply": string, "requires_review"?: boolean }` |

- Todo en **snake_case** y **UTF-8**.
- Login sin `Authorization`; chat **con** `Authorization: Bearer <token>`.

---

## Checklist de implementación

- [ ] Paso 1: CORS y variables de entorno configurados.
- [ ] Paso 2: `POST /auth/login` devuelve `{ "access_token": "..." }`; 401 para credenciales incorrectas.
- [ ] Paso 3: Dependencia que valida `Authorization: Bearer <token>` y lanza 401 si falla.
- [ ] Paso 4: `POST /agent/chat` exige auth, recibe `message` (y opcionalmente `conversation_id`), devuelve `reply` y `requires_review`.
- [ ] Paso 5: Routers montados y servidor en el puerto 8000.

Cuando todo esté listo, en el frontend activa el login real en `LoginPage` (descomentar la llamada a `loginApi` y `setToken(data.access_token)`); el chat ya está conectado y funcionará en cuanto el backend responda con el formato indicado.
