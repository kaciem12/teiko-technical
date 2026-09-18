"""
load_data.py

Reads cell-count.csv and loads it into a SQLite database (teiko.db)
using three tables instead of one flat table:

    subjects     - one row per person
    samples      - one row per sample drawn from a person
    cell_counts  - one row per (sample, cell population) measurement

Why three tables: in the raw CSV, a subject's age/sex/condition/treatment
are repeated on every row for that subject. That is redundant and makes it
possible for the same subject to end up with conflicting values. Splitting
the data so each fact is stored exactly once removes that risk, and the
long format for cell counts means adding a new cell population later is a
new row rather than a schema change.

Run:  python load_data.py
"""

import os
import sqlite3
import pandas as pd

CSV_PATH = "cell-count.csv"
DB_PATH = "teiko.db"

# the five measured cell populations in the CSV
POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def create_schema(conn):
    """Drop and recreate the tables so the script can be re-run safely."""
    conn.executescript("""
        DROP TABLE IF EXISTS cell_counts;
        DROP TABLE IF EXISTS samples;
        DROP TABLE IF EXISTS subjects;

        CREATE TABLE subjects (
            subject     TEXT PRIMARY KEY,
            project     TEXT,
            condition   TEXT,
            age         INTEGER,
            sex         TEXT,
            treatment   TEXT,
            response    TEXT
        );

        CREATE TABLE samples (
            sample                      TEXT PRIMARY KEY,
            subject                     TEXT NOT NULL,
            sample_type                 TEXT,
            time_from_treatment_start   INTEGER,
            FOREIGN KEY (subject) REFERENCES subjects(subject)
        );

        CREATE TABLE cell_counts (
            sample      TEXT NOT NULL,
            population  TEXT NOT NULL,
            count       INTEGER,
            PRIMARY KEY (sample, population),
            FOREIGN KEY (sample) REFERENCES samples(sample)
        );
    """)


def main():
    df = pd.read_csv(CSV_PATH)
    print("loaded %d rows from %s" % (len(df), CSV_PATH))

    # --- subjects: one row per subject ---------------------------------
    subject_cols = ["subject", "project", "condition", "age",
                    "sex", "treatment", "response"]
    subjects = df[subject_cols].drop_duplicates()

    # sanity check: a subject should appear only once after dedup.
    # if not, the same subject has conflicting values somewhere.
    dupes = subjects["subject"].duplicated().sum()
    if dupes:
        raise ValueError("%d subjects have conflicting attributes" % dupes)

    # --- samples: one row per sample -----------------------------------
    sample_cols = ["sample", "subject", "sample_type",
                   "time_from_treatment_start"]
    samples = df[sample_cols].drop_duplicates()

    if samples["sample"].duplicated().sum():
        raise ValueError("duplicate sample ids with different attributes")

    # --- cell_counts: wide -> long -------------------------------------
    # the CSV has one column per population; melt turns those five columns
    # into five rows per sample, so the table is (sample, population, count)
    cell_counts = df.melt(
        id_vars=["sample"],
        value_vars=POPULATIONS,
        var_name="population",
        value_name="count",
    )

    # --- write to sqlite -----------------------------------------------
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    create_schema(conn)

    subjects.to_sql("subjects", conn, if_exists="append", index=False)
    samples.to_sql("samples", conn, if_exists="append", index=False)
    cell_counts.to_sql("cell_counts", conn, if_exists="append", index=False)

    conn.commit()

    for table in ["subjects", "samples", "cell_counts"]:
        n = conn.execute("SELECT COUNT(*) FROM %s" % table).fetchone()[0]
        print("%-12s %d rows" % (table, n))

    conn.close()
    print("wrote %s" % DB_PATH)


if __name__ == "__main__":
    main()