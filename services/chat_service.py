"""
Lógica del chat: interfaz mínima para el agente de IA.

Por ahora devuelve una respuesta stub. Cuando el servicio de IA esté disponible,
reemplazar la implementación por una llamada HTTP (o SDK) que envíe el prompt
y parsee la respuesta a (reply, requires_review). La firma de esta función
se mantiene para no cambiar el router.
"""


def obtener_respuesta_agente(
    prompt: str,
    conversation_id: str | None = None,
    contexto_usuario: dict | None = None,
) -> tuple[str, bool]:
    """
    Devuelve (reply, requires_review).

    Stub actual: respuesta fija. Futuro: llamar al servicio de IA externo
    con el prompt (y opcionalmente conversation_id y contexto_usuario).
    """
    # TODO: Conectar aquí el servicio de IA (enviar prompt, recibir respuesta).
    _ = conversation_id
    _ = contexto_usuario
    reply = (
        "Gracias por tu mensaje. Este es un asistente de prueba. "
        "Cuando se conecte el servicio de IA, aquí recibirás una respuesta personalizada."
    )
    requires_review = False
    return reply, requires_review
