import yaml
import requests
import pandas as pd
import duckdb
import os
from io import BytesIO
from urllib.parse import urlparse

# Load data_sources.yml
yaml_path = os.path.join(os.path.dirname(__file__), 'data_sources.yml')
with open(yaml_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

data_sources = config['data_sources']

# Prepare DuckDB connection and expected table names
cache_dir = os.path.join(os.path.dirname(__file__), 'data_sources.cache')
os.makedirs(cache_dir, exist_ok=True)
db_path = os.path.join(os.path.dirname(__file__), 'landing.duckdb')
con = duckdb.connect(db_path)
expected_tables = {f"{ds['name'].replace('-', '_')}" for ds in data_sources}

# Drop any landing tables not listed in data_sources.yml
existing_tables = con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main';").fetchall()
for (tbl,) in existing_tables:
    if tbl not in expected_tables:
        print(f"Dropping table not in data_sources.yml: {tbl}")
        con.execute(f"DROP TABLE IF EXISTS {tbl}")

for ds in data_sources:
    url = ds['url']
    name = ds['name']
    file_format = ds['format']
    filename = os.path.basename(url)
    cache_path = os.path.join(cache_dir, filename)

    # Use local file if it exists, otherwise try to download
    if os.path.exists(cache_path):
        print(f"Using cached file: {cache_path}")
        with open(cache_path, 'rb') as f:
            file_content = f.read()
    else:
        print(f"Downloading file from: {url}")
        parsed_url = urlparse(url)
        referer = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": referer,
            "Connection": "keep-alive"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        file_content = response.content
        with open(cache_path, 'wb') as f:
            f.write(file_content)

    # Read Excel file into DataFrame using pandas only
    if file_format == "xlsx":
        format_options = ds.get("format_options", {})
        sheet_name = format_options.get("sheet_name")
        skip_rows = format_options.get("skip_rows")
        # Pass skiprows if provided, else default to None
        read_excel_kwargs = {"sheet_name": sheet_name}
        if skip_rows is not None:
            read_excel_kwargs["skiprows"] = skip_rows
        df = pd.read_excel(BytesIO(file_content), **read_excel_kwargs)
        # If header_rename is provided, replace columns with header_rename
        header_rename = format_options.get("header_rename")
        if header_rename:
            df.columns = header_rename
        else:
            df.columns = [str(col) for col in df.columns]
    else:
        df = pd.read_excel(BytesIO(file_content))

    # Write to DuckDB landing table
    safe_name = name.replace('-', '_')
    table_name = f"{safe_name}"
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    print(f"Ingested '{name}' into DuckDB table '{table_name}' in '{db_path}'")

con.close()
