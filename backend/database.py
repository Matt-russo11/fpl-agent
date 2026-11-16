"""
database.py - Saves each scout report to a SQLite database so trends can be
analyzed across gameweeks with SQL.

SQLite is a database that lives in a single file (scout_history.db) next to
this script. Python includes it, so there is nothing to install.

Two tables:
  scout_runs        one row per scout report (when it ran, which gameweek)
  shortlist_players one row per player on that report's scout shortlist
The run_id column links each player row back to the report it came from.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).with_name("scout_history.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read columns by name, like row["player_name"]
    return conn


def init_db():
    """Create the tables if they don't exist yet. Safe to run every time the app starts."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scout_runs (
                run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date    TEXT    NOT NULL,   -- YYYY-MM-DD
                run_time    TEXT    NOT NULL,   -- full UTC timestamp
                target_gw   INTEGER NOT NULL,   -- gameweek the report is for
                manager_id  TEXT
            );

            CREATE TABLE IF NOT EXISTS shortlist_players (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id       INTEGER NOT NULL REFERENCES scout_runs(run_id),
                player_id    INTEGER NOT NULL,
                player_name  TEXT    NOT NULL,
                team         TEXT    NOT NULL,
                position     TEXT    NOT NULL,  -- GK, DEF, MID or FWD
                position_rank INTEGER NOT NULL, -- 1 = best at that position
                cost         REAL,              -- in millions
                form         REAL,
                ep_next      REAL,              -- FPL expected points next gameweek
                score        REAL               -- form + ep_next (the scout's ranking score)
            );
        """)


def save_scout_report(report):
    """
    Save a scout report's shortlist. Saves at most one report per gameweek per day,
    so refreshing the page doesn't fill the database with duplicates.
    Returns the new run_id, or None if today's report for this gameweek is already saved.
    """
    if not report or "error" in report or not report.get("scout_shortlist"):
        return None

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    target_gw = report.get("target_gw")

    with get_connection() as conn:
        # WHERE filters rows: is there already a report for this gameweek today?
        existing = conn.execute(
            "SELECT run_id FROM scout_runs WHERE target_gw = ? AND run_date = ?",
            (target_gw, today),
        ).fetchone()
        if existing:
            return None

        # INSERT adds a new row
        cur = conn.execute(
            "INSERT INTO scout_runs (run_date, run_time, target_gw, manager_id) VALUES (?, ?, ?, ?)",
            (today, now.isoformat(timespec="seconds"), target_gw, str(report.get("manager_id"))),
        )
        run_id = cur.lastrowid

        rows = []
        for position, players in report["scout_shortlist"].items():
            for rank, p in enumerate(players, start=1):
                rows.append((
                    run_id, p["id"], p["name"], p["team"], position, rank,
                    _num(p.get("cost")), _num(p.get("form")), _num(p.get("ep_next")), _num(p.get("score")),
                ))
        conn.executemany(
            """INSERT INTO shortlist_players
               (run_id, player_id, player_name, team, position, position_rank, cost, form, ep_next, score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        return run_id


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Analysis queries. Each one asks the database a question in SQL.
# ---------------------------------------------------------------------------

def most_shortlisted_players(limit=10):
    """Which players make the shortlist most often? (COUNT + GROUP BY + ORDER BY)"""
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            """
            SELECT player_name, team, position,
                   COUNT(*)              AS times_shortlisted,
                   ROUND(AVG(score), 1)  AS avg_score
            FROM shortlist_players
            GROUP BY player_id
            ORDER BY times_shortlisted DESC, avg_score DESC
            LIMIT ?
            """,
            (limit,),
        )]


def team_averages():
    """Which teams supply the most shortlisted players, and how strong are they? (GROUP BY + AVG)"""
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            """
            SELECT team,
                   COUNT(*)                AS shortlist_spots,
                   ROUND(AVG(ep_next), 2)  AS avg_expected_points
            FROM shortlist_players
            GROUP BY team
            ORDER BY shortlist_spots DESC
            """
        )]


def player_history(name):
    """How has one player's ranking changed over time? (JOIN two tables + WHERE)"""
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            """
            SELECT r.target_gw, r.run_date, p.position, p.position_rank, p.form, p.ep_next, p.score
            FROM shortlist_players AS p
            JOIN scout_runs AS r ON r.run_id = p.run_id
            WHERE p.player_name LIKE ?
            ORDER BY r.run_time
            """,
            (f"%{name}%",),
        )]


def best_value_picks(max_cost, limit=10):
    """Best scorers under a budget in the most recent report. (WHERE with a subquery)"""
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            """
            SELECT player_name, team, position, cost, score
            FROM shortlist_players
            WHERE cost <= ?
              AND run_id = (SELECT MAX(run_id) FROM scout_runs)
            ORDER BY score DESC
            LIMIT ?
            """,
            (max_cost, limit),
        )]


def report_count():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM scout_runs").fetchone()[0]
