# Backend MediAgent

API REST en FastAPI para MediAgent: autenticación de pacientes (login JWT) y chat con un agente de IA. La base de datos es una carpeta de JSONs que se lee en tiempo de ejecución.

---

## Requisitos

- Python 3.10+
- Dependencias en `requirements.txt` (FastAPI, uvicorn, python-jose, passlib, etc.)

---

## Instalación

```bash
# Clonar (o estar en la raíz del repo)
cd backend-mediagent

# Crear entorno virtual e instalar
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Variables de entorno (opcional)
cp .env.example .env
# Editar .env: CORS_ORIGINS, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
```

---

## Cómo se usa

### Arrancar el servidor (recomendado: Docker)

La forma **recomendada** para usar el backend es con **Docker**: evita instalar Python y dependencias a mano y es la misma en todos los entornos.

```bash
docker compose up --build
```

- API: **http://localhost:8000**
- Documentación: **http://localhost:8000/docs**
- Health: **http://localhost:8000/health**

### Arrancar sin Docker (local)

Si prefieres correr el servidor sin Docker (con Python y un entorno virtual):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El puerto 8000 se expone igual. Puedes usar un `.env` para configurar CORS y SECRET_KEY.

### Variables de entorno

| Variable | Descripción | Por defecto |
|----------|--------------|-------------|
| `CORS_ORIGINS` | Orígenes permitidos (coma-separados). Usar `*` para permitir cualquier origen. | `http://localhost:8080` |
| `SECRET_KEY` | Clave para firmar los JWT. | (valor por defecto en código; en producción usar una clave segura) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de validez del token. | `60` |

---

## Estructura del proyecto

```
backend-mediagent/
├── main.py              # App FastAPI, CORS, routers, GET /health
├── config.py            # Variables de entorno (CORS, SECRET_KEY, etc.)
├── dependencies.py      # get_current_user (Bearer token → usuario)
├── requirements.txt
├── .env.example
├── routers/
│   ├── auth.py          # POST /auth/login
│   └── agent.py         # POST /agent/chat
├── schemas/
│   ├── auth.py          # LoginRequest, LoginResponse
│   └── chat.py          # ChatRequest, ChatResponse
├── services/
│   ├── db.py            # Lectura de los JSON en bd/
│   ├── auth_service.py  # Validación de credenciales y JWT
│   └── chat_service.py  # Lógica del chat (stub; aquí se conecta el agente IA)
└── bd/                  # “Base de datos” (archivos JSON)
    ├── pacientes.json
    ├── doctores.json
    ├── especialidades.json
    ├── sedes.json
    ├── sede_especialidades.json
    └── horarios.json
```

---

## Endpoints

| Método | Ruta | Autenticación | Descripción |
|--------|------|----------------|-------------|
| GET | `/health` | No | Health check. Respuesta: `{"status": "ok"}`. |
| POST | `/auth/login` | No | Login de paciente. |
| POST | `/agent/chat` | Sí (Bearer) | Envía un mensaje al agente y recibe respuesta. |

### POST `/auth/login`

- **Body:** `{ "email": string, "password": string }`
- **200:** `{ "access_token": string }`
- **401:** Credenciales inválidas (`detail: "Credenciales inválidas"`).
- **422:** Body inválido (falta email/password o tipo incorrecto).

### POST `/agent/chat`

- **Headers:** `Authorization: Bearer <access_token>`
- **Body:** `{ "message": string, "conversation_id"?: string }`
- **200:** `{ "reply": string, "requires_review": boolean }` (por defecto `requires_review: false`).
- **401:** Token ausente o inválido.
- **422:** Body inválido (p. ej. `message` faltante).

---

## Base de datos (carpeta `bd/`)

La “base de datos” son archivos JSON en la carpeta **`bd/`**. El backend los lee en cada petición (sin cachear), así que los cambios en los archivos se reflejan al instante.

### Archivos y contenido

| Archivo | Contenido |
|---------|-----------|
| **pacientes.json** | Lista de pacientes. Campos: `id`, `nombres`, `apellidos`, `correo`, `contrasena_hash`, `distrito`, `especialidad_id`, `enfermedad`. Usado para login. |
| **doctores.json** | Doctores. Campos: `id`, `nombres`, `apellidos`, `especialidad_id`, `sede_id`, `numero_colegiatura`. |
| **especialidades.json** | Especialidades. Campos: `id`, `nombre`. |
| **sedes.json** | Sedes/clínicas. Campos: `id`, `nombre`, `distrito`, `distritos_cercanos`, `direccion`, `telefono`. |
| **sede_especialidades.json** | Relación sede–especialidad. Campos: `id`, `sede_id`, `especialidad_id`. |
| **horarios.json** | Turnos por doctor. Campos: `id`, `doctor_id`, `fecha`, `hora_inicio`, `hora_fin`, `estado` (`disponible` / `ocupado`). |

### Relaciones

- **Paciente** → `especialidad_id` → especialidad.
- **Doctor** → `especialidad_id`, `sede_id` → especialidad y sede.
- **Sede** ↔ **Especialidad**: muchos a muchos vía `sede_especialidades.json`.
- **Horario** → `doctor_id` → doctor.

En `services/db.py` hay funciones para leer cada archivo: `get_paciente_por_correo`, `get_paciente_por_id`, `get_doctores()`, `get_especialidades()`, `get_sedes()`, `get_sede_especialidades()`, `get_horarios()`.

### Cuentas de prueba (pacientes)

Con los hashes **simulados** actuales en `pacientes.json`, todos los pacientes aceptan la misma contraseña de desarrollo:

- **Contraseña:** `password123`
- **Correos de ejemplo:**  
  `daniel.garcia@gmail.com`, `sofia.ramirez@gmail.com`, `luis.huaman@gmail.com`, `camila.flores@gmail.com`, `javier.morales@gmail.com`

Cuando reemplaces los hashes por **bcrypt reales**, cada paciente tendrá su propia contraseña.

---

## Integrar el Agente de IA

El chat está preparado para conectar un servicio de IA externo (prompt → respuesta). Todo el cambio se hace en **`services/chat_service.py`**.

### Qué hay ahora

- Función **`obtener_respuesta_agente(prompt, conversation_id=None, contexto_usuario=None)`**.
- Devuelve **`(reply: str, requires_review: bool)`**.
- Implementación actual: **stub** (respuesta fija, `requires_review=False`).

### Qué hay que hacer para conectar el agente

1. **Mantener la firma**  
   No cambiar el nombre ni los argumentos de `obtener_respuesta_agente` ni el tipo de retorno `(str, bool)`, para no tocar `routers/agent.py`.

2. **Dónde llamar al servicio de IA**  
   Dentro de `obtener_respuesta_agente`:
   - Construir el **prompt** (o mensaje) a partir de `prompt` (mensaje del usuario) y, si quieres, de `contexto_usuario` (datos del paciente: enfermedad, especialidad, etc.) y de `conversation_id` (historial).
   - Llamar por HTTP (o SDK) al servicio de IA.
   - Parsear la respuesta del servicio y obtener:
     - **Texto de respuesta** → `reply`.
     - **Si debe revisión humana** → `requires_review` (por regla de negocio o campo que devuelva el servicio).

3. **Contexto de usuario**  
   `contexto_usuario` es el dict del paciente (tal como viene de `pacientes.json`): `id`, `nombres`, `apellidos`, `correo`, `distrito`, `especialidad_id`, `enfermedad`, etc. Puedes usarlo para personalizar el prompt o las reglas.

4. **Conversation_id**  
   Opcional: si tu servicio de IA mantiene historial por conversación, envía `conversation_id` en la petición para continuar el hilo.

5. **Errores y timeouts**  
   Si el servicio de IA falla o no responde, decidir qué devolver (mensaje de fallback, `requires_review=True`) o lanzar una excepción para que FastAPI devuelva 5xx.

6. **Configuración**  
   Si la URL o la API key del servicio de IA son configurables, usar variables de entorno (y `config.py`) en lugar de valores fijos en código.

Resumen: la integración se hace **solo en `chat_service.py`**, manteniendo la misma interfaz `(prompt, conversation_id, contexto_usuario) → (reply, requires_review)`.
