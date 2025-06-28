# Economic Data Dashboard

This project provides tools to ingest, validate, and visualize New Zealand economic data (e.g., GDP, credit conditions) using DuckDB and Streamlit.

## Quick Start

### 1. Clone the Repository

```
git clone https://github.com/Teutenberg/econ_dashboard.git
cd econ_dashboard
```

### 2. Set Up a Virtual Environment

Run the provided PowerShell script (Windows):

```
powershell -ExecutionPolicy Bypass -File setup_venv.ps1
```

Or manually:

```
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Ingest Data

Download and ingest the data sources into DuckDB:

```
python ingest_duckdb.py
```

This will create/update `landing.duckdb` in the project folder.

### 4. Validate Data (Optional)

To check table structure and export sample rows:

```
python validate/validate_duckdb.py
```

### 5. Run the Streamlit App

Start the dashboard:

```
streamlit run streamlit_app.py
```

This will open a browser window with interactive plots.

---

## Project Structure

- `ingest_duckdb.py` — Downloads and ingests Excel data into DuckDB.
- `validate/validate_duckdb.py` — Validates DuckDB tables and exports samples.
- `data_sources.yml` — Configuration for data sources.
- `requirements.txt` — Python dependencies.
- `setup_venv.ps1` — PowerShell script to set up the virtual environment.
- `data_sources.cache/` — Cached Excel files.
- `landing.duckdb` — DuckDB database file.
- `streamlit_app.py` — Streamlit dashboard for data visualization.

## Notes

- Requires Python 3.8+.
- All data is sourced from the Reserve Bank of New Zealand.
- Manually download latest data and place files in `data_sources.cache` directory.
- If you add new data sources, update `data_sources.yml` and re-run `ingest_duckdb.py`.
