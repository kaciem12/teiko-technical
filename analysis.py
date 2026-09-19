import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

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

# PART THREE
    # One table where each row is:
        # A sample
        # A cell population
        # It's percentage
        # Whether the patient responded

    # Which samples are in this cohort, and did the patient respond?

def get_miraclib_pbmc_cohort(conn):
    query = """
    SELECT sm.sample, sb.response
    FROM samples AS sm
    JOIN subjects AS sb ON sm.subject = sb.subject
    WHERE sb.condition = 'melanoma'
        AND sb.treatment = 'miraclib'
        AND sm.sample_type = 'PBMC'
    """
    return pd.read_sql_query(query, conn)

    # Drawing what we have
        # hue = "response" splits each pop into 2 side by side boxes, one per group
        # savefig writes to a file
def plot_response_comparison(merged):
    sns.boxplot(data=merged, x='population', y='percentage', hue='response')
    plt.title("Cell population frequencies: responders vs non-responders")
    plt.ylabel("Relative frequency (%)")
    plt.tight_layout()
    plt.savefig("response_boxplot.png")

# Comparing Responders Function
def compare_responders(merged):
    # An empty list to collect one result per pop
    results = []
    # Gives the 5 distinct pop names. Loop runs once per name
    for population in merged["population"].unique():
        # pandas filtering, produces T/F for every row, outer bracket keeps only T
        subset = merged[merged["population"] == population]
        # split responders & non responders, "percentage" pulls out just that column
        responders = subset[subset["response"] == "yes"]["percentage"]
        non_responders = subset[subset["response"] == "no"]["percentage"]
        # two sample t-test, returns 2 values at once, catches in order
        t_stat, p_value = stats.ttest_ind(responders, non_responders, equal_var=False)
        # Adds one row's worth of findings to the list
        results.append({
            "population": population,
            "mean_responders": responders.mean(),
            "mean_non_responders": non_responders.mean(),
            "p_value": p_value,
            "significant": p_value < 0.05,
        })
        # turns list of results into a table
    return pd.DataFrame(results)


# PART FOUR

    # Question 1 : Identify all melanoma PBMC samples at baseline from patients treated with miraclib.
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
    cohort = get_miraclib_pbmc_cohort(conn)
    print(len(cohort))
    freq = get_frequencies(conn)
    merged = freq.merge(cohort, on='sample')
    print(len(merged))
    print(merged.head())
    plot_response_comparison(merged)
    stats_table = compare_responders(merged)
    print(stats_table)