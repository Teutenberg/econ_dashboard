"""
Ingest Excel data sources into DuckDB using configuration from data_sources.yml.
"""
import yaml
import pandas as pd
import duckdb
import os
from io import BytesIO


def load_data_sources_config():
    yaml_path = os.path.join('data_sources', 'data_sources.yml')
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['data_sources']


def ingest_to_duckdb(data_sources, db_path, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    with duckdb.connect(db_path) as con:
        expected_tables = {f"{ds['name'].replace('-', '_')}" for ds in data_sources}
        # Drop tables not in config
        existing_tables = con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main';").fetchall()
        for (tbl,) in existing_tables:
            if tbl not in expected_tables:
                print(f"Dropping table not in data_sources.yml: {tbl}")
                con.execute(f"DROP TABLE IF EXISTS {tbl}")
        for ds in data_sources:
            name = ds['name']
            file_format = ds['format']
            url = ds['url']
            filename = os.path.basename(url)
            cache_path = os.path.join(cache_dir, filename)
            if not os.path.exists(cache_path):
                print(f"Missing required file: {cache_path}. Please download it first.")
                print("Hint: Run 'powershell -ExecutionPolicy Bypass -File download_data_sources.ps1' to download missing files.")
                continue
            print(f"Using cached file: {cache_path}")
            with open(cache_path, 'rb') as f:
                file_content = f.read()
            if file_format == "xlsx":
                format_options = ds.get("format_options", {})
                sheet_name = format_options.get("sheet_name")
                skip_rows = format_options.get("skip_rows")
                read_excel_kwargs = {"sheet_name": sheet_name}
                if skip_rows is not None:
                    read_excel_kwargs["skiprows"] = skip_rows
                df = pd.read_excel(BytesIO(file_content), **read_excel_kwargs)
                header_rename = format_options.get("header_rename")
                if header_rename:
                    df.columns = header_rename
                else:
                    df.columns = [str(col) for col in df.columns]
            else:
                df = pd.read_excel(BytesIO(file_content))
            table_name = name.replace('-', '_')
            con.execute(f"DROP TABLE IF EXISTS {table_name}")
            con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
            print(f"Ingested '{name}' into DuckDB table '{table_name}' in '{db_path}'")


def main():
    data_sources = load_data_sources_config()
    cache_dir = os.path.join(os.path.dirname(__file__), 'data_sources')
    db_path = os.path.join(os.path.dirname(__file__), 'landing.duckdb')
    ingest_to_duckdb(data_sources, db_path, cache_dir)


if __name__ == '__main__':
    main()
