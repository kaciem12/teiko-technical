import pandas as pd
import sqlite3

def get_frequencies(conn):
    query = """
    WITH sample_totals AS (
        SELECT sample, SUM(count) AS total_count
        FROM cell_counts AS c 
        GROUP BY sample
    )
    SELECT
        c.sample,
        t.total_count,
        c.population,
        c.count,
        100.0 * c.count / t.total_count AS percentage
    FROM cell_counts AS c
    JOIN sample_totals AS t ON c.sample = t.sample
    """
    return pd.read_sql_query(query, conn)

if __name__ == "__main__":
    conn = sqlite3.connect("teiko.db")
    result = get_frequencies(conn)
    print(result.head())
    print(len(result))
