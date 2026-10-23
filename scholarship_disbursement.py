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
    row = conn.execute(
        "SELECT amount FROM awards WHERE id = ?", (award_id,)
    ).fetchone()
    if row is None:
        return None
    conn.execute("UPDATE awards SET disbursed = 1 WHERE id = ?", (award_id,))
    conn.commit()
    return row[0]


def total_disbursed():
    return conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1"
    ).fetchone()[0]


def archive():
    logger.info("archiving awards")


def by_scheme_count(scheme):
    if scheme is None:
        return 0
    return conn.execute(
        "SELECT COUNT(*) FROM awards WHERE scheme = ?", (scheme,)
    ).fetchone()[0]


def main():
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(by_scheme_count("Merit"), total_disbursed())
    archive()


if __name__ == "__main__":
    main()