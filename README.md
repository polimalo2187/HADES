# 🔥 HADES Forex Signals Bot

HADES es un bot profesional de señales Forex diseñado para ofrecer
**señales de alta calidad**, no cantidad.

---

## 🧠 Características principales

- Análisis de mercado 24/7
- Scoring cuantitativo estricto
- Solo las 3 mejores señales del mercado
- Planes: Free / Plus / Premium
- Señales personalizadas por usuario
- Protección anti-copia
- MongoDB como base de datos
- Telegram desacoplado del motor

---

## 📦 Arquitectura

- `engine/` → análisis y generación de señales
- `signal_manager/` → gestión y clasificación
- `services/` → lógica de negocio
- `telegram_bot/` → interfaz Telegram
- `scheduler/` → tareas automáticas
- `scripts/` → arranque independiente

---

## 🚀 Ejecución

### Local
```bash
pip install -r requirements.txt
python scripts/start_engine.py
python scripts/start_bot.py
