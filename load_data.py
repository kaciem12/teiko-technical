# 1) read cell-count.csv into a data fram
# 2) Connect SQLite database file and create the three tables
# 3) Build subjects table - one row per sample
# 4) Build samples table - one row per sampls
# 5) Build cell_counts - one row per sample AND population
# 6) Write all 3 into database

import pandas as pd
import sqlite3
# 2) Connection I run SQL through
conn = sqlite3.connect("teiko.db")

# Step 1
data = pd.read_csv("cell-count.csv") #Gives you a DataFrame

# 3) Subjects table
subjects = data[["age", "subject", "sex", "treatment", "response", "condition", "project"]].drop_duplicates()
print("subjects:", len(subjects))

# 4) Samples table
samples = data[["subject", "sample", "sample_type", "time_from_treatment_start"]].drop_duplicates()
print("samples:", len(samples))

# 5) Build cell_counts
    # RN 5 cell types are in 5 diff columns 
    # Want as rows
cell_counts = data.melt(
    id_vars=["sample"], # keep sample as a label in every row
    value_vars=["b_cell", "cd8_t_cell", "nk_cell", "monocyte", "cd4_t_cell"], #Columns to unstack into rows
    var_name="population", # old column names
    value_name="count" # old numbers need a column
)
print("cell counts:", len(cell_counts))

# Create Tables
    # PRIMARY KEY -> what rows must be unique?
    # FOREIGN KEY -> does this value exist in another table/connects?
# Subjects Table
    # Drop first so script can rerun w/o errors
    # Reverse order of creation bc of foreign keys
conn.executescript("""
DROP TABLE IF EXISTS subjects;
CREATE TABLE subjects (
    subject TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT,
    condition TEXT,
    project TEXT,
    PRIMARY KEY (subject)
);
""")
subjects.to_sql("subjects", conn, if_exists="append", index=False)

# Samples table
conn.executescript("""
DROP TABLE IF EXISTS samples;
CREATE TABLE samples (
    subject TEXT,
    sample TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    PRIMARY KEY (sample),
    FOREIGN KEY (subject) REFERENCES subjects(subject)
);
""")
samples.to_sql("samples", conn, if_exists="append", index=False)

# Cell_counts table
conn.executescript("""
DROP TABLE IF EXISTS cell_counts;
CREATE TABLE cell_counts (
    sample TEXT,
    population TEXT,
    count INTEGER,
    PRIMARY KEY (sample, population),
    FOREIGN KEY (sample) REFERENCES samples(sample)
);
""")
cell_counts.to_sql("cell_counts", conn, if_exists="append", index=False)

conn.commit()

print(pd.read_sql("SELECT COUNT(*) FROM subjects", conn))
print(pd.read_sql("SELECT COUNT(*) FROM samples", conn))
print(pd.read_sql("SELECT COUNT(*) FROM cell_counts", conn))
