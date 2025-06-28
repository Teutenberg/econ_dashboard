import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Economic Data Plots", layout="wide")

# Set up paths
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'landing.duckdb')

def plot_table(table_name, N=8):
    db_con = duckdb.connect(db_path)
    try:
        df = db_con.execute(f'SELECT * FROM {table_name}').fetchdf()
    except Exception as e:
        st.error(f'Error querying table {table_name}: {e}')
        db_con.close()
        return
    db_con.close()

    # Try to find a date or time column automatically
    possible_date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'period' in col.lower()]
    if possible_date_cols:
        date_col = possible_date_cols[0]
    else:
        date_col = df.columns[0]

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df.set_index(date_col)

    value_cols = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
    if not value_cols:
        st.warning(f'No numeric columns found to plot in {table_name}.')
        return
    top_cols = df[value_cols].var().sort_values(ascending=False).head(N).index.tolist()
    markers = ['o', 's', 'D', '^', 'v', 'X', '*', 'P']
    fig, ax = plt.subplots(figsize=(14, 7))
    for i, col in enumerate(top_cols):
        marker = markers[i % len(markers)]
        ax.plot(df.index, df[col], label=col, linewidth=2, linestyle='-', marker=marker, markersize=7)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f'Time Series from {table_name} (Top {N} by variance)')
    ax.set_xlabel(date_col)
    ax.set_ylabel('Value')
    ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize='small')
    plt.tight_layout(rect=[0, 0, 0.8, 1])
    st.pyplot(fig)

st.title("Economic Data Plot Dashboard")

# List of tables to plot
plot_tables = [
    'CREDIT_CONDITIONS_C60',
    'GROSS_DOMESTIC_PRODUCT_M5',
]

for table in plot_tables:
    st.header(table)
    plot_table(table)
