import os
from plot_utils import plot_duckdb_table

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'landing.duckdb')
    table_name = 'GROSS_DOMESTIC_PRODUCT_M5'
    try:
        fig = plot_duckdb_table(db_path, table_name)
    except Exception as e:
        print(e)
        return
    import matplotlib.pyplot as plt
    plt.show()

if __name__ == '__main__':
    main()
