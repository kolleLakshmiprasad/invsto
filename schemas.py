from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class StockSchema(BaseModel):
    date: datetime
    open: Decimal  # Renamed to match the model
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int  # Use `int` for integer values

    class Config:
        from_attributes = True