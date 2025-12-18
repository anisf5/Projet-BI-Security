
import pandas as pd
from data_helpers import fetch_from_access
from database_manager import clear_tables, load_data

def run_etl_pipeline():
    print("--- Starting ETL Pipeline (Access -> SQL Server) ---")
    

    raw_customers = fetch_from_access("SELECT * FROM Customers")
    raw_employees = fetch_from_access("SELECT * FROM Employees")
    raw_orders = fetch_from_access("SELECT * FROM Orders")
    

    
 
    dim_customers = raw_customers.rename(columns={
        "ID": "CustomerId",
        "Company": "CompanyName",
        "Country/Region": "Country"
    })[["CustomerId", "CompanyName", "City", "Country"]]

    dim_customers = dim_customers.fillna("Unknown")
    dim_customers["CustomerId"] = dim_customers["CustomerId"].astype(str)


    dim_employees = raw_employees.rename(columns={
        "ID": "EmployeeId",
        "First Name": "FirstName",
        "Last Name": "LastName",
        "Country/Region": "Country"
    })[["EmployeeId", "FirstName", "LastName", "City", "Country"]]
    
    dim_employees = dim_employees.fillna("Unknown")
    dim_employees["EmployeeId"] = dim_employees["EmployeeId"].astype(str)

    raw_orders["OrderDate_Parsed"] = pd.to_datetime(raw_orders["Order Date"])
    unique_dates = pd.Series(raw_orders["OrderDate_Parsed"].dropna().unique()).sort_values()
    
    dim_date = pd.DataFrame({"FullDate": unique_dates})
    dim_date["DateId"] = dim_date["FullDate"].dt.strftime("%Y%m%d").astype(int)
    dim_date["Day"] = dim_date["FullDate"].dt.day
    dim_date["Month"] = dim_date["FullDate"].dt.month
    dim_date["MonthName"] = dim_date["FullDate"].dt.strftime("%B")
    dim_date = dim_date.drop_duplicates(subset=["DateId"])
 
    
    fact_orders = raw_orders.copy()
    fact_orders["OrderId"] = fact_orders["Order ID"].astype(int)
    fact_orders["CustomerId"] = fact_orders["Customer ID"].fillna(-1).astype(int).astype(str) 
    fact_orders["EmployeeId"] = fact_orders["Employee ID"].fillna(-1).astype(int).astype(str)

    fact_orders["DateId"] = fact_orders["OrderDate_Parsed"].apply(
        lambda x: int(x.strftime("%Y%m%d")) if pd.notna(x) else None
    )

    fact_orders["DeliveredFlag"] = fact_orders["Shipped Date"].notna().astype(int)
    
    fact_orders = fact_orders[["OrderId", "CustomerId", "EmployeeId", "DateId", "DeliveredFlag"]]
    
    valid_custs = set(dim_customers["CustomerId"])
    valid_emps = set(dim_employees["EmployeeId"])
    valid_dates = set(dim_date["DateId"])

    initial_count = len(fact_orders)
    fact_orders = fact_orders[
        fact_orders["CustomerId"].isin(valid_custs) & 
        fact_orders["EmployeeId"].isin(valid_emps) &
        fact_orders["DateId"].isin(valid_dates)
    ]
    dropped = initial_count - len(fact_orders)
    if dropped > 0:
        print(f"[WARN] Dropped {dropped} orders due to missing foreign keys.")


    clear_tables()
    load_data(dim_customers, dim_employees, dim_date, fact_orders)
    print("--- ETL Finished Successfully ---")
