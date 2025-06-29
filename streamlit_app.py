import streamlit as st
import os
from plot_utils import plot_duckdb_table
import matplotlib.pyplot as plt

st.set_page_config(page_title="Economic Data Plots", layout="wide")

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'landing.duckdb')

st.title("Economic Data Plot Dashboard")

plot_tables = [
    'CREDIT_CONDITIONS_C60',
    'GROSS_DOMESTIC_PRODUCT_M5',
    'DOMESTIC_TRADE_M4'
]

for table in plot_tables:
    st.header(table)
    try:
        fig = plot_duckdb_table(db_path, table)
        st.pyplot(fig)
    except Exception as e:
        st.error(str(e))
