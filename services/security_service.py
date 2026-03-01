# services/security_service.py

from __future__ import annotations

from core.logger import get_logger
from services.user_service import UserService

logger = get_logger(__name__)


class SecurityService:
    """
    Servicio de seguridad y cumplimiento de políticas.
    Maneja advertencias, violaciones y bloqueos automáticos.
    """

    def __init__(self):
        self.user_service = UserService()

    def register_policy_violation(self, user_id: int):
        logger.warning(f"Violación de política detectada | Usuario: {user_id}")
        self.user_service.increment_policy_violation(user_id)

    def get_policies_text(self) -> str:
        return (
            "🔐 POLÍTICAS DE SEGURIDAD – HADES\n\n"
            "Las señales proporcionadas por HADES son de uso estrictamente personal.\n"
            "Está prohibido copiar, reenviar, compartir o redistribuir cualquier señal,\n"
            "total o parcialmente, por cualquier medio.\n\n"
            "El uso indebido de las señales, así como cualquier intento de abuso del sistema,\n"
            "resultará en el bloqueo permanente e irreversible de la cuenta.\n\n"
            "HADES se reserva el derecho de suspender o bloquear cuentas sin previo aviso\n"
            "cuando se detecten violaciones a estas políticas.\n\n"
            "Al utilizar este bot, aceptas estas condiciones."
        )


# ─────────────────────────────────────────────────────────────
# WRAPPER para scripts/maintenance.py
# ─────────────────────────────────────────────────────────────

_security_singleton = SecurityService()


def cleanup_blocked_users():
    """
    En este repo no hay una política de "limpieza" real más allá de bloquear.
    Este wrapper existe para que scripts/maintenance.py no truene.
    Si luego quieres: aquí podemos desactivar push para usuarios bloqueados, etc.
    """
    logger.info("cleanup_blocked_users(): no-op (placeholder)")
    return True
