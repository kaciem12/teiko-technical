import pandas as pd
import sqlite3

# PART TWO

# define a function Get Frequencies, conn is the parameter
    # query """ holds text
    # Each sample has 5 types of cells, so 5 counts
        # GROUP BY sample -> gathers 5 rows into one group
        # SUM(count) adds them
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

    #FROM cell_counts AS c & JOIN... -> Find the row in sample_totals w/ the same sample id, and attach its columns

    return pd.read_sql_query(query, conn) # Pandas, take this SQL text, give me back results as a table


# PART FOUR

# New function Get Baseline Samples, conn is parameter
    # query holds text

def get_baseline_samples(conn):
    query = """
    SELECT sm.sample, sm.subject, sb.project, sb.response, sb.sex
    FROM samples AS sm
    JOIN subjects AS sb ON sm.subject = sb.subject
    WHERE sb.condition = 'melanoma'
        AND sb.treatment = 'miraclib'
        AND sm.sample_type = 'PBMC'
        AND sm.time_from_treatment_start = 0
    """
    return pd.read_sql_query(query, conn)


# Only run the next few lines if the file is being run directly
if __name__ == "__main__":
    conn = sqlite3.connect("teiko.db") # open database, store connection in conn
    result = get_frequencies(conn) # call the function, give it conn, runs, stored as result
    print(result.head()) # Show the first 5 rows
    print(len(result)) # Show total row count
    baseline = get_baseline_samples(conn)
    print(baseline.head())
    print(len(baseline))
    print(baseline["project"].value_counts())
    print(baseline["response"].value_counts())
    print(baseline["sex"].value_counts())