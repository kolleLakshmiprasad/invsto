from sqlalchemy import Column, Integer, Float, DateTime, DECIMAL
from database import Base

class Stock(Base):
    __tablename__ = "stock"

    date = Column(DateTime, primary_key=True, index=True)
    open= Column(DECIMAL, index=True)  # Renamed to avoid conflict with SQL keyword
    high = Column(DECIMAL, index=True)
    low = Column(DECIMAL)
    close = Column(DECIMAL)
    volume = Column(DECIMAL)
