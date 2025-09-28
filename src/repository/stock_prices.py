import logging
from typing import List, Dict, Optional, Tuple
from datetime import date
from psycopg2.extras import RealDictCursor
from src.config.db_config import DatabaseConfig

logger = logging.getLogger(__name__)

class OhlcvRepository:
    def __init__(self):
        self.conn = None

    def _connect_to_db(self):
        if not self.conn:
            self.conn = DatabaseConfig.get_connection()
        return self.conn

    def add_or_update_ohlcv(self, symbol: str, rows: List[Dict]):
        """
        Insert or update OHLCV rows for a stock symbol.
        """
        try:
            conn = self._connect_to_db()
            cur = conn.cursor()
            for row in rows:
                cur.execute(
                    """
                    INSERT INTO ohlcv_daily 
                        (symbol, date, open, high, low, close, adjusted_close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, date) DO UPDATE
                    SET open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        adjusted_close = EXCLUDED.adjusted_close,
                        volume = EXCLUDED.volume;
                    """,
                    (
                        symbol,
                        row["date"],
                        row["open"],
                        row["high"],
                        row["low"],
                        row["close"],
                        row["adjusted_close"],
                        row["volume"],
                    ),
                )
            conn.commit()
            cur.close()
        except Exception as e:
            logger.error(f"Error saving OHLCV data: {e}")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None

    def get_range(self, symbol: str, start_date: date, end_date: date) -> List[Dict]:
        """
        Get OHLCV data for a symbol in a date range.
        """
        rows = []
        try:
            conn = self._connect_to_db()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT * FROM ohlcv_daily
                WHERE symbol = %s AND date BETWEEN %s AND %s
                ORDER BY date ASC;
                """,
                (symbol, start_date, end_date),
            )
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            logger.error(f"Error reading OHLCV range: {e}")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
        return rows

    def get_all(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all OHLCV data (for a symbol or the whole DB).
        """
        rows = []
        try:
            conn = self._connect_to_db()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            if symbol:
                cur.execute("SELECT * FROM ohlcv_daily WHERE symbol = %s;", (symbol,))
            else:
                cur.execute("SELECT * FROM ohlcv_daily;")
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            logger.error(f"Error reading all OHLCV data: {e}")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
        return rows

    def get_last_entry_date(self, symbol: str) -> Optional[date]:
        """
        Get the most recent date for which we have OHLCV data for a stock.
        """
        result = None
        try:
            conn = self._connect_to_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(date) FROM ohlcv_daily WHERE symbol = %s;", (symbol,)
            )
            result = cur.fetchone()[0]
            cur.close()
        except Exception as e:
            logger.error(f"Error reading last entry date: {e}")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
        return result

    def delete_symbol(self, symbol: str):
        """
        Delete all OHLCV data for a stock.
        """
        try:
            conn = self._connect_to_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM ohlcv_daily WHERE symbol = %s;", (symbol,))
            conn.commit()
            cur.close()
        except Exception as e:
            logger.error(f"Error deleting symbol {symbol}: {e}")
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
