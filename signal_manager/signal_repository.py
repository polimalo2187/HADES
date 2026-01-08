# signal_manager/signal_repository.py

from datetime import datetime
from core.database import MongoDB
from core.logger import get_logger
from core.constants import (
    SIGNAL_ACTIVE,
    SIGNAL_CANCELLED,
    SIGNAL_EXPIRED,
)

logger = get_logger(__name__)


class SignalRepository:
    """
    Repositorio de señales.
    Controla persistencia, vigencia y unicidad de señales por plan.
    """

    COLLECTION_NAME = "signals"

    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db[self.COLLECTION_NAME]

    def get_active_signal_by_plan(self, plan: str) -> dict | None:
        """
        Retorna la señal activa actual para un plan.
        """
        return self.collection.find_one(
            {
                "plan": plan,
                "status": SIGNAL_ACTIVE,
            }
        )

    def expire_old_signals(self):
        """
        Marca como vencidas las señales que superaron su expires_at.
        """
        now = datetime.utcnow()

        result = self.collection.update_many(
            {
                "status": SIGNAL_ACTIVE,
                "expires_at": {"$lte": now},
            },
            {"$set": {"status": SIGNAL_EXPIRED}},
        )

        if result.modified_count > 0:
            logger.info(
                f"Señales vencidas automáticamente: {result.modified_count}"
            )

    def cancel_signal(self, signal_id: str):
        """
        Cancela manualmente una señal activa.
        """
        self.collection.update_one(
            {"id": signal_id},
            {"$set": {"status": SIGNAL_CANCELLED}},
        )

    def save_new_signal(self, signal: dict):
        """
        Guarda una nueva señal como activa.
        """
        self.collection.insert_one(signal)

        logger.info(
            f"Señal guardada | Par: {signal['pair']} | Plan: {signal['plan']}"
        )
