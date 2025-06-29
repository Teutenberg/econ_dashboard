import duckdb
import yaml
import os

# Load data_sources.yml from the parent directory of this script
yaml_path = os.path.join('data_sources', 'data_sources.yml')
with open(yaml_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

db_path = 'landing.duckdb'

con = duckdb.connect(db_path)

# Validate each data source listed in data_sources.yml
for ds in config['data_sources']:
    name = ds['name']
    table_name = f"{name.replace('-', '_')}"
    print(f"\nValidating table: {table_name}")
    # Print table DDL
    try:
        ddl_rows = con.execute(f"PRAGMA show_tables; PRAGMA table_info('{table_name}');").fetchall()
        # Try DuckDB's recommended way: PRAGMA table_info
        columns = con.execute(f"PRAGMA table_info('{table_name}')").fetchdf()
        col_defs = ",\n  ".join(f"{row['name']} {row['type']}" for _, row in columns.iterrows())
        ddl = f"CREATE TABLE {table_name} (\n  {col_defs}\n);"
        print(f"DDL for {table_name}:\n{ddl}")
    except Exception as e:
        print(f"Error getting DDL for {table_name}: {e}")
    # Print first 10 rows and column names as a formatted table
    try:
        df = con.execute(f"SELECT * FROM {table_name} LIMIT 10").fetchdf()
        # Export first 10 rows to CSV in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_filename = os.path.join(script_dir, f"{table_name}_sample.csv")
        df.to_csv(csv_filename, index=False)
        print(f'Exported first 10 rows to {csv_filename}')
        # Print row count
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f'Row count: {count}')
    except Exception as e:
        print(f"Error querying {table_name}: {e}")

con.close()
