# scripts/start_bot.py

from core.logger import get_logger
from telegram_bot.bot import run_bot

logger = get_logger(__name__)


def main():
    logger.info("🤖 Iniciando Bot de Telegram HADES")
    run_bot()


if __name__ == "__main__":
    main()
