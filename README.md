# teiko-technical

Dashboard URL: https://teiko-technical-eb42gxsenqffrb6rzf38mm.streamlit.app/

## How to run it

Three commands, in order, in the terminal:

```bash
make setup      # installs dependencies
make pipeline   # builds the database and runs the analysis
make dashboard  # starts the dashboard on port 8501
```

teiko.db is generated output and is not committed. app.py builds it if missing, so the dashboard works from a fresh clone.

## Files

- `load_data.py` — Part 1. Schema and data loading
- `analysis.py` — Parts 2, 3, and 4, one function each
- `app.py` — Streamlit dashboard

## Schema

- subjects (one row per person)
- samples (one row per blood sample)
- cell_counts (one row per sample and population)
- The CSV repeats each subject's age, sex, condition and treatment on all 3 of their rows. Storing them once removes the chance of the same subject having conflicting values
- Cell counts are long, not wide. A 6th population would be a new row instead of a schema change
- Primary keys prevent duplicates
- Foreign keys prevent a sample referencing a subject that does not exist

## Part 3: Responders vs Non Responders

Melanoma patients on miraclib, PBMC samples, all timepoints. 1,968 samples from 656 subjects. Two sample t-test with Welch's correction.

| population | responders | non-responders | p value |
|---|---|---|---|
| b_cell | 9.80% | 10.00% | 0.171 |
| **cd4_t_cell** | **30.54%** | **29.90%** | **0.005** |
| cd8_t_cell | 24.88% | 24.94% | 0.768 |
| monocyte | 19.94% | 20.08% | 0.466 |
| nk_cell | 14.84% | 15.07% | 0.193 |

- cd4_t_cell is the only significant difference. Since I ran 5 tests, I lowered the threshold from 0.05 to 0.01 to account for the extra chances of a false positive. cd4_t_cell's p value of 0.005 still clears it.
- But the difference is small. Responders averaged 30.54% and non-responders 29.90%, a gap of 0.64 percentage points. In the boxplot the two groups almost completely overlap.
- So cd4_t_cell is not useful as a predictor. The difference between the groups is real, but it is far too small to tell whether any individual patient will respond to miraclib.

## Part 4: Baseline subset

Melanoma PBMC samples at baseline from miraclib patients: 656 samples from 656