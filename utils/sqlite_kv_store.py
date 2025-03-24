import sqlite3
import threading
import logging
import os
import atexit
from typing import Optional, Any, Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLiteKeyValueStore:
    """
    Thread-safe SQLite key-value store with lazy initialization and default values.
    Uses singleton pattern to ensure single database connection.
    """
    
    _instance = None
    _init_lock = threading.Lock()
    _db_lock = threading.Lock()
    
    # Configuration
    APP_DATA = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
    APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
    DB_PATH = os.path.join(APP_DIRECTORY, "kv_store.db")
    
    # Default values (only inserted if keys don't exist)
    _DEFAULT_VALUES = {
        "US_MODE": "true",
        "DIGICERT_API_KEY_US": "",
        "DIGICERT_API_KEY_EU": "",
        "DIGICERT_BASE_URL_US": "https://www.digicert.com/services/v2",
        "DIGICERT_BASE_URL_EU": "https://certcentral.digicert.eu/services/v2",
        "CSR": "",
        "PRIVATE_KEY": "",
        "ORG_ID": "",
        "API_TIMEOUT": "30",
        "MAX_RETRIES": "3"
    }

    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Lazy initialization - actual setup happens on first use"""
        if not hasattr(self, '_initialized'):
            self._initialized = False

    def _ensure_initialized(self):
        """Thread-safe lazy initialization"""
        if not self._initialized:
            with self._init_lock:
                if not self._initialized:
                    try:
                        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
                        self.conn = sqlite3.connect(
                            self.DB_PATH,
                            check_same_thread=False,
                            timeout=30.0,
                            isolation_level=None
                        )
                        self.conn.execute("PRAGMA journal_mode=WAL")
                        self.conn.execute("PRAGMA synchronous=NORMAL")
                        self._create_table()
                        self._initialize_defaults()
                        self._initialized = True
                        atexit.register(self.close)
                        logger.info(f"Initialized SQLite database at {self.DB_PATH}")
                    except Exception as e:
                        logger.error(f"Database initialization failed: {str(e)}")
                        raise

    def _create_table(self):
        """Create the key-value table if it doesn't exist"""
        with self._db_lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    def _initialize_defaults(self):
        """Insert default values only for missing keys"""
        with self._db_lock:
            for key, value in self._DEFAULT_VALUES.items():
                self.conn.execute("""
                    INSERT OR IGNORE INTO kv_store (key, value)
                    VALUES (?, ?)
                """, (key, value))
            self.conn.commit()
        logger.info("Initialized default values")

    # CRUD Operations
    def set(self, key: str, value: Any) -> None:
        """Set/update a key-value pair"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO kv_store (key, value)
                    VALUES (?, ?)
                """, (key, str(value)))
                self.conn.commit()
                logger.debug(f"Set key: {key}")
            except sqlite3.Error as e:
                logger.error(f"Error setting key {key}: {str(e)}")
                raise

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get value for a key, return default if not found"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                cursor = self.conn.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else default
            except sqlite3.Error as e:
                logger.error(f"Error getting key {key}: {str(e)}")
                return default

    def delete(self, key: str) -> None:
        """Delete a key-value pair"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                self.conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
                self.conn.commit()
                logger.debug(f"Deleted key: {key}")
            except sqlite3.Error as e:
                logger.error(f"Error deleting key {key}: {str(e)}")
                raise

    # Bulk operations
    def set_many(self, items: Dict[str, Any]) -> None:
        """Set multiple key-value pairs in a transaction"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                self.conn.execute("BEGIN TRANSACTION")
                for key, value in items.items():
                    self.conn.execute("""
                        INSERT OR REPLACE INTO kv_store (key, value)
                        VALUES (?, ?)
                    """, (key, str(value)))
                self.conn.commit()
                logger.debug(f"Set {len(items)} keys")
            except sqlite3.Error as e:
                self.conn.rollback()
                logger.error(f"Error in set_many: {str(e)}")
                raise

    # Query operations
    def keys(self) -> List[str]:
        """Get all keys"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                cursor = self.conn.execute("SELECT key FROM kv_store")
                return [row[0] for row in cursor.fetchall()]
            except sqlite3.Error as e:
                logger.error(f"Error getting keys: {str(e)}")
                return []

    def values(self) -> List[Any]:
        """Get all values"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                cursor = self.conn.execute("SELECT value FROM kv_store")
                return [row[0] for row in cursor.fetchall()]
            except sqlite3.Error as e:
                logger.error(f"Error getting values: {str(e)}")
                return []

    def items(self) -> List[Tuple[str, Any]]:
        """Get all key-value pairs"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                cursor = self.conn.execute("SELECT key, value FROM kv_store")
                return cursor.fetchall()
            except sqlite3.Error as e:
                logger.error(f"Error getting items: {str(e)}")
                return []

    def exists(self, key: str) -> bool:
        """Check if a key exists"""
        self._ensure_initialized()
        with self._db_lock:
            try:
                cursor = self.conn.execute("SELECT 1 FROM kv_store WHERE key = ?", (key,))
                return cursor.fetchone() is not None
            except sqlite3.Error as e:
                logger.error(f"Error checking existence of key {key}: {str(e)}")
                return False

    def close(self) -> None:
        """Close the database connection"""
        if hasattr(self, 'conn'):
            try:
                self.conn.close()
                logger.info("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing database: {str(e)}")

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()


# Singleton instance - safe to import anywhere
kv_store = SQLiteKeyValueStore()
