import duckdb
import pandas as pd
import matplotlib.pyplot as plt

def plot_duckdb_table(db_path, table_name, N=8, ax=None):
    """
    Plots the top N numeric columns by variance from a DuckDB table.
    Args:
        db_path (str): Path to DuckDB database.
        table_name (str): Table name to plot.
        N (int): Number of columns to plot.
        ax (matplotlib.axes.Axes, optional): Axis to plot on. If None, creates new figure.
    Returns:
        matplotlib.figure.Figure: The figure object.
    """
    db_con = duckdb.connect(db_path)
    try:
        df = db_con.execute(f'SELECT * FROM {table_name}').fetchdf()
    except Exception as e:
        db_con.close()
        raise RuntimeError(f'Error querying table {table_name}: {e}')
    db_con.close()

    # Find date/time column
    possible_date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'period' in col.lower()]
    date_col = possible_date_cols[0] if possible_date_cols else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df.set_index(date_col)

    value_cols = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
    if not value_cols:
        raise ValueError(f'No numeric columns found to plot in {table_name}.')
    top_cols = df[value_cols].var().sort_values(ascending=False).head(N).index.tolist()
    markers = ['o', 's', 'D', '^', 'v', 'X', '*', 'P']
    if ax is None:
        fig, ax = plt.subplots(figsize=(14, 7))
    else:
        fig = ax.figure
    for i, col in enumerate(top_cols):
        marker = markers[i % len(markers)]
        ax.plot(df.index, df[col], label=col, linewidth=2, linestyle='-', marker=marker, markersize=7)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f'Time Series from {table_name} (Top {N} by variance)')
    ax.set_xlabel(date_col)
    ax.set_ylabel('Value')
    ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize='small')
    fig.tight_layout(rect=[0, 0, 0.8, 1])
    return fig
