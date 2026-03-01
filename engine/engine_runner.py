# engine/engine_runner.py

import time
from core.logger import get_logger
from engine.market_data import MarketDataProvider
from engine.indicators import IndicatorEngine
from engine.signal_scoring import SignalScorer
from engine.signal_generator import SignalGenerator
from signal_manager.signal_repository import SignalRepository
from signal_manager.signal_cleanup import SignalCleanup
from core.constants import PLAN_FREE, PLAN_PLUS, PLAN_PREMIUM

logger = get_logger(__name__)


class EngineRunner:
    """
    Ejecuta el motor de análisis de mercado 24/7.
    Independiente de Telegram.

    ✅ En este repo YA existe PushNotificationsService.
    Para que el push funcione aunque corras start_engine.py (sin scheduler),
    disparamos push al final del ciclo cuando se crea una señal nueva.
    """

    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self.running = False

        self.market_data = MarketDataProvider()
        self.indicators = IndicatorEngine()
        self.scorer = SignalScorer()
        self.generator = SignalGenerator()
        self.signal_repo = SignalRepository()
        self.signal_cleanup = SignalCleanup()

    def start(self):
        logger.info("🔥 HADES Engine iniciado (modo 24/7)")
        self.running = True

        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.exception(f"❌ Error en ciclo del engine: {e}")

            time.sleep(self.interval_seconds)

    def stop(self):
        self.running = False
        logger.info("🛑 HADES Engine detenido")

    def run_cycle(self):
        """
        Ciclo completo de análisis:
        - Limpia señales expiradas
        - Analiza mercado
        - Genera hasta 3 señales (una por plan)
        - Si hubo señal nueva: dispara push "Nueva señal disponible" por plan exacto (sin incluir señal)
        """
        logger.info("🔁 Iniciando ciclo de análisis")

        self.signal_cleanup.cleanup_expired_signals()

        active_plans = {
            PLAN_FREE: self.signal_repo.get_active_signal_by_plan(PLAN_FREE),
            PLAN_PLUS: self.signal_repo.get_active_signal_by_plan(PLAN_PLUS),
            PLAN_PREMIUM: self.signal_repo.get_active_signal_by_plan(PLAN_PREMIUM),
        }

        created_any_signal = False

        for pair in self.market_data.get_supported_pairs():
            candles = self.market_data.fetch_latest_data(pair)

            if not candles or len(candles) < 50:
                continue

            indicators = self.indicators.calculate(candles)
            score = self.scorer.score(indicators)

            if not self.scorer.is_tradeable(score):
                continue

            signal = self.generator.generate(
                pair=pair,
                candles=candles,
                indicators=indicators,
                score=score,
            )

            if not signal:
                continue

            plan = signal["plan"]

            if active_plans.get(plan):
                continue

            self.signal_repo.save_new_signal(signal)
            active_plans[plan] = signal
            created_any_signal = True

            logger.info(f"🚨 Señal {plan.upper()} generada | {pair} | Score {score}")

            if all(active_plans.values()):
                break

        # ✅ Push only if something new was created
        if created_any_signal:
            try:
                from services.push_notifications_service import PushNotificationsService

                stats = PushNotificationsService().run()
                logger.info(
                    "🔔 Push disparado por señal nueva | sent=%s failed=%s dup=%s no_chat=%s inactive=%s plans=%s",
                    stats.get("sent"),
                    stats.get("failed"),
                    stats.get("skipped_duplicate"),
                    stats.get("skipped_no_chat_id"),
                    stats.get("skipped_inactive"),
                    stats.get("plans"),
                )
            except Exception as e:
                logger.exception(f"❌ Error disparando push: {e}")

        logger.info("✅ Ciclo finalizado")


# ─────────────────────────────────────────────────────────────
# WRAPPER para scheduler/jobs.py
# ─────────────────────────────────────────────────────────────

_engine_singleton = EngineRunner(interval_seconds=60)


def run_engine():
    """
    Ejecuta un ciclo único del engine (no loop infinito).
    """
    return _engine_singleton.run_cycle()
