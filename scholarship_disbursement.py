"""Scholarship disbursement module.

Records scholarship awards in an in-memory SQLite database, marks them as
disbursed, and reports simple per-scheme statistics.
"""
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE awards ("
    "id INTEGER PRIMARY KEY, "
    "student TEXT, "
    "scheme TEXT, "
    "amount INTEGER, "
    "disbursed INTEGER)"
)


def grant(student, scheme, amount, audit=None):
    """Record a new award and append the student to the audit list."""
    if audit is None:
        audit = []
    conn.execute(
        "INSERT INTO awards (student, scheme, amount, disbursed) "
        "VALUES (?, ?, ?, 0)",
        (student, scheme, amount),
    )
    conn.commit()
    audit.append(student)
    return audit


def disburse(award_id):
    """Mark an award as disbursed and return its amount (None if missing)."""
    row = conn.execute(
        "SELECT amount FROM awards WHERE id = ?", (award_id,)
    ).fetchone()
    if row is None:
        return None
    conn.execute("UPDATE awards SET disbursed = 1 WHERE id = ?", (award_id,))
    conn.commit()
    return row[0]


def total_disbursed():
    """Return the total amount of all awards disbursed so far."""
    return conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1"
    ).fetchone()[0]


def archive():
    """Log that the awards are being archived."""
    logger.info("archiving awards")


def by_scheme_count(scheme):
    """Return the number of awards under the given scheme."""
    if scheme is None:
        return 0
    return conn.execute(
        "SELECT COUNT(*) FROM awards WHERE scheme = ?", (scheme,)
    ).fetchone()[0]


def main():
    """Run a small demo of granting, disbursing and archiving awards."""
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(by_scheme_count("Merit"), total_disbursed())
    archive()


if __name__ == "__main__":
    main()
    