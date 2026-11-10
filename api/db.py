import sqlite3, os

DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "offres.db")
)

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS offres (
            id     TEXT PRIMARY KEY,
            titre  TEXT,
            ent    TEXT,
            lieu   TEXT,
            desc   TEXT,
            lien   TEXT,
            date   TEXT,
            score  INTEGER,
            rais   TEXT,
            statut TEXT    DEFAULT 'Non traité',
            favori INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS runs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
            nb_offres INTEGER,
            status    TEXT,
            message   TEXT
        );
    """)
    conn.commit()
    conn.close()

def upsert_offres(offres: list):
    """Insère ou met à jour les offres en préservant statut/favori définis par l'utilisateur."""
    conn = _connect()
    for o in offres:
        conn.execute("""
            INSERT INTO offres (id, titre, ent, lieu, desc, lien, date, score, rais)
            VALUES (:id, :titre, :ent, :lieu, :desc, :lien, :date, :score, :rais)
            ON CONFLICT(id) DO UPDATE SET
                titre = excluded.titre,
                ent   = excluded.ent,
                lieu  = excluded.lieu,
                desc  = excluded.desc,
                lien  = excluded.lien,
                date  = excluded.date,
                score = excluded.score,
                rais  = excluded.rais
        """, o)
    conn.commit()
    conn.close()

def get_offres() -> list:
    conn = _connect()
    rows = conn.execute(
        "SELECT id, titre, ent, lieu, desc, lien, date, score, rais "
        "FROM offres WHERE score > 0 ORDER BY score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_run(nb_offres: int, status: str, message: str = ""):
    conn = _connect()
    conn.execute(
        "INSERT INTO runs (nb_offres, status, message) VALUES (?, ?, ?)",
        (nb_offres, status, message)
    )
    conn.commit()
    conn.close()

def db_exists() -> bool:
    return os.path.exists(DB_PATH)
