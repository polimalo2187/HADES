# data_feeder/server.py

from fastapi import FastAPI, HTTPException
from data_feeder.schemas import PriceTick
from core.logger import get_logger
from core.database import MongoDB

logger = get_logger(__name__)
app = FastAPI(title="HADES MT5 Data Feeder")

# Colección donde se guarda el último precio por símbolo
db = MongoDB.get_db()
prices_collection = db["prices"]


@app.post("/mt5/price")
def receive_price(tick: PriceTick):
    """
    Endpoint para recibir precios desde MT5 (o cualquier feeder externo).
    Guarda el último precio por símbolo en MongoDB.
    """
    try:
        payload = tick.model_dump() if hasattr(tick, "model_dump") else tick.dict()
        prices_collection.update_one(
            {"symbol": tick.symbol},
            {"$set": payload},
            upsert=True,
        )
        return {"status": "ok", "symbol": tick.symbol}
    except Exception as e:
        logger.exception(f"Error guardando tick: {e}")
        raise HTTPException(status_code=500, detail="Error guardando tick")
