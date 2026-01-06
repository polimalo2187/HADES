# data_feeder/server.py

from fastapi import FastAPI, HTTPException
from data_feeder.schemas import PriceTick
from core.logger import get_logger
from core.database import mongo_client

logger = get_logger(__name__)
app = FastAPI(title="HADES MT5 Data Feeder")

# Colección donde se guarda el último precio por símbolo
prices_collection = mongo_client.hades.prices


@app.post("/mt5/price")
def receive_price(price: PriceTick):
    """
    Endpoint que recibe precios desde MT5
    """

    try:
        prices_collection.update_one(
            {"symbol": price.symbol},
            {
                "$set": {
                    "symbol": price.symbol,
                    "bid": price.bid,
                    "ask": price.ask,
                    "timestamp": price.timestamp,
                }
            },
            upsert=True,
        )

        logger.info(
            f"📡 Precio recibido {price.symbol} | bid={price.bid} ask={price.ask}"
        )
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Error recibiendo precio: {e}")
        raise HTTPException(status_code=500, detail="Error storing price")
