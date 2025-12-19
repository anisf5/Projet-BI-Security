import os
import pandas as pd
import pyodbc
from settings import DATA_DIR, SQL_SERVER, SQL_DATABASE, SQL_DRIVER
from data_helpers import fetch_from_access
from database_manager import get_sql_conn_str

def export_access_to_csv(export_dir):
    print("--- Exporting Access Data ---")
    tables = {
        "Customers": "SELECT * FROM Customers",
        "Employees": "SELECT * FROM Employees",
        "Orders": "SELECT * FROM Orders"
    }
    
    for table_name, query in tables.items():
        print(f"Exporting {table_name} from Access...")
        df = fetch_from_access(query)
        if not df.empty:
            file_path = os.path.join(export_dir, f"access_{table_name.lower()}.csv")
            df.to_csv(file_path, index=False)
            print(f"Saved to {file_path}")
        else:
            print(f"No data found for {table_name} in Access.")

def export_sql_to_csv(export_dir):
    print("\n--- Exporting SQL Server Data ---")
    conn_str = f"DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;"
    
    tables = [
        "DimCustomer",
        "DimEmployee",
        "DimDate",
        "FactOrders"
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        for table in tables:
            print(f"Exporting {table} from SQL Server...")
            query = f"SELECT * FROM {table}"
            df = pd.read_sql(query, conn)
            if not df.empty:
                file_path = os.path.join(export_dir, f"sql_{table.lower()}.csv")
                df.to_csv(file_path, index=False)
                print(f"Saved to {file_path}")
            else:
                print(f"No data found for {table} in SQL Server.")
        conn.close()
    except Exception as e:
        print(f"[ERROR] SQL Server export failed: {e}")

if __name__ == "__main__":
    export_dir = os.path.join(DATA_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    export_access_to_csv(export_dir)
    export_sql_to_csv(export_dir)
    
    print("\n--- Export Completed ---")
