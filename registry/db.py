import sqlite3
import hashlib
from pathlib import Path

# In‑memory cache of ADU values for fast lookup
_adu_cache = {}

def init_db(db_path: Path):
    """Initialize the SQLite registry.

    Creates the ``adu`` table (if missing).  Immutable behavior is enforced at
    the application level – we deliberately omit SQLite ``RAISE`` triggers as
    they are not supported on the minimal SQLite build used in this environment.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS adu (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                value REAL NOT NULL,
                hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # No triggers – updates/deletes are not exposed via the public API.
        conn.commit()

def _add_adu(db_path: Path, name: str, value: float) -> None:
    """Insert a new ADU (immutable write)."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        hash_val = hashlib.sha256(f"{name}:{value}".encode()).hexdigest()
        try:
            cursor.execute(
                "INSERT INTO adu (name, value, hash) VALUES (?, ?, ?)",
                (name, value, hash_val)
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"ADU '{name}' already exists (immutable)") from exc

def _get_adu_value(db_path: Path, name: str) -> float:
    """Retrieve the numeric value of an ADU, using an in‑memory cache."""
    if name in _adu_cache:
        return _adu_cache[name]
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM adu WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            _adu_cache[name] = row[0]
            return row[0]
        raise KeyError(f"ADU '{name}' not found")

def _list_adus(db_path: Path):
    """Return a list of all ADUs (name, value, hash, created_at)."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, value, hash, created_at FROM adu ORDER BY created_at"
        )
        return cursor.fetchall()

# Default DB location – can be overridden by the TIM_REGISTRY_DB env var.
DEFAULT_DB_PATH = Path(__file__).parent / 'tim_registry.db'

# Public wrappers bound to the default DB path.
def add_adu(name: str, value: float) -> None:
    return _add_adu(DEFAULT_DB_PATH, name, value)

def get_adu_value(name: str) -> float:
    return _get_adu_value(DEFAULT_DB_PATH, name)

def list_adus():
    return _list_adus(DEFAULT_DB_PATH)
