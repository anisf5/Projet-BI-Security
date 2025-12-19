# data_helpers.py
import pyodbc
import pandas as pd
from settings import ACCESS_DB_PATH, ACCESS_DRIVER

def get_access_connection():
    """Establishes connection to the Access Database."""
    conn_str = f"DRIVER={{{ACCESS_DRIVER}}};DBQ={ACCESS_DB_PATH};"
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"[ERROR] Connection to Access failed: {e}")
        raise

def fetch_from_access(query):
    """Executes a SQL query against Access DB and returns a DataFrame."""
    try:
        conn = get_access_connection()
        print(f"[Access] Executing: {query}")
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return pd.DataFrame()

def get_employees():
    """Fetches list of employees from Access."""
    query = "SELECT ID, [First Name] & ' ' & [Last Name] AS FullName FROM Employees"
    return fetch_from_access(query)

def get_employee_orders(employee_id):
    """Fetches orders for a specific employee from Access."""
    query = f"""
        SELECT O.[Order ID], O.[Order Date], O.[Shipped Date], C.Company AS CustomerName
        FROM Orders O
        LEFT JOIN Customers C ON O.[Customer ID] = C.ID
        WHERE O.[Employee ID] = {employee_id}
    """
    return fetch_from_access(query)
