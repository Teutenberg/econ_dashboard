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

### 3. Download Data Sources

Run the PowerShell script to download the latest data files using Microsoft Edge:

```
powershell -ExecutionPolicy Bypass -File data_sources\download_data_sources.ps1
```

> **Note:** The script will open Edge tabs for each file and close them after download. Files are saved to `data_sources/`.

### 4. Ingest Data

Ingest the downloaded data sources into DuckDB:

```
python ingest_duckdb.py
```

This will create/update `landing.duckdb` in the project folder.

### 5. Validate Data (Optional)

To check table structure and export sample rows:

```
python validate/validate_duckdb.py
```

### 6. Run the Streamlit App

Start the dashboard:

```
streamlit run streamlit_app.py
```

This will open a browser window with interactive plots.

---

## Project Structure

- `ingest_duckdb.py` — Ingests Excel data into DuckDB from config.
- `validate/validate_duckdb.py` — Validates DuckDB tables and exports samples.
- `data_sources.yml` — Configuration for data sources.
- `requirements.txt` — Python dependencies.
- `setup_venv.ps1` — PowerShell script to set up the virtual environment.
- `data_sources/` — Cached Excel files and download script.
- `landing.duckdb` — DuckDB database file.
- `streamlit_app.py` — Streamlit dashboard for data visualization.
- `plot_utils.py` — Shared plotting utility for DuckDB tables.
- `plot_*.py` — Standalone scripts for plotting individual tables.

## Notes

- Requires Python 3.8+.
- All data is sourced from the Reserve Bank of New Zealand.
- Use the provided download script to fetch the latest data files.
- If you add new data sources, update `data_sources.yml` and re-run `ingest_duckdb.py`.

## Troubleshooting

- **Edge browser required:** The download script uses Microsoft Edge to fetch files. Ensure Edge is installed and available in your PATH.
- **File not downloading:** If a file does not appear in `data_sources/`, check your Downloads folder and move it manually if needed.
- **Permission issues:** Run PowerShell as Administrator if you encounter permission errors.
- **Virtual environment issues:** Ensure you activate the virtual environment before running Python scripts.
