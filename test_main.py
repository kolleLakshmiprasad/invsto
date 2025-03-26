import unittest
from fastapi.testclient import TestClient
from main import app, moving_average_strategy
from database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Stock
import datetime

# Setup Test Database (Use SQLite in-memory for testing)
DATABASE_URL = "postgresql://postgres@localhost:5432/stock_market"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables for testing
Stock.metadata.create_all(bind=engine)

# Create a test client
client = TestClient(app)

class TestFastAPITradingStrategy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Set up test database with mock data """
        db: Session = TestingSessionLocal()
        stock_data = [
            Stock(date=datetime.datetime(2024, 3, 1), close=100.0),
            Stock(date=datetime.datetime(2024, 3, 2), close=102.0),
            Stock(date=datetime.datetime(2024, 3, 3), close=101.0),
            Stock(date=datetime.datetime(2024, 3, 4), close=105.0),
            Stock(date=datetime.datetime(2024, 3, 5), close=108.0),
            Stock(date=datetime.datetime(2024, 3, 6), close=110.0),
            Stock(date=datetime.datetime(2024, 3, 7), close=107.0),
            Stock(date=datetime.datetime(2024, 3, 8), close=109.0),
        ]
        db.add_all(stock_data)
        db.commit()
        db.close()

    def test_get_strategy_performance(self):
        """ Test if the strategy endpoint returns correct structure """
        response = client.get("/strategy/performance")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_return", data)
        self.assertIn("buy_signals", data)
        self.assertIn("sell_signals", data)

    def test_moving_average_calculation(self):
        """ Test if moving averages are calculated correctly """
        db = TestingSessionLocal()
        result = moving_average_strategy(db, short_window=3, long_window=5)
        db.close()
        self.assertIsInstance(result, dict)
        self.assertIn("total_return", result)

    def test_invalid_data_submission(self):
        """ Test invalid data input """
        invalid_data = {"date": "invalid-date", "close": "NaN"}
        response = client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
