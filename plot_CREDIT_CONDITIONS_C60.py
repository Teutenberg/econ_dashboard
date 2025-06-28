import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import os

# Set up paths
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'landing.duckdb')

table_name = 'landing_CREDIT_CONDITIONS_C60'

# Connect to DuckDB and load data
db_con = duckdb.connect(db_path)

# List available tables
print('Available tables:')
tables = db_con.execute("SHOW TABLES").fetchdf()
print(tables)

# Query all data from the table
try:
    df = db_con.execute(f'SELECT * FROM {table_name}').fetchdf()
except Exception as e:
    print(f'Error querying table {table_name}:', e)
    db_con.close()
    exit(1)
db_con.close()

# --- User should customize the following section for their time series ---
# Try to find a date or time column automatically
possible_date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'period' in col.lower()]
if possible_date_cols:
    date_col = possible_date_cols[0]
else:
    # Fallback: use the first column
    date_col = df.columns[0]

# Convert to datetime if possible
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df = df.dropna(subset=[date_col])

# Set date as index
df = df.set_index(date_col)

# Plot all columns except the index (date)
value_cols = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
# Plot only the top N columns by variance for readability
N = 8  # Number of lines to plot
if not value_cols:
    print('No numeric columns found to plot.')
else:
    # Select top N columns by variance
    top_cols = df[value_cols].var().sort_values(ascending=False).head(N).index.tolist()
    # Define a list of marker symbols to cycle through
    markers = ['o', 's', 'D', '^', 'v', 'X', '*', 'P']
    ax = plt.figure(figsize=(14, 7)).gca()
    for i, col in enumerate(top_cols):
        marker = markers[i % len(markers)]
        ax.plot(df.index, df[col], label=col, linewidth=2, linestyle='-', marker=marker, markersize=7)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    plt.title(f'Time Series from {table_name} (Top {N} by variance)')
    plt.xlabel(date_col)
    plt.ylabel('Value')
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize='small')
    plt.tight_layout(rect=[0, 0, 0.8, 1])
    plt.show()
