# data_feeder/schemas.py

from pydantic import BaseModel
from datetime import datetime


class PriceTick(BaseModel):
    symbol: str
    bid: float
    ask: float
    timestamp: datetime
