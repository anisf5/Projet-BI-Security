
import pandas as pd
from data_helpers import fetch_from_access
from database_manager import clear_tables, load_data
from settings import DATA_DIR
import os

def run_etl_pipeline():
    print("--- Starting ETL Pipeline (Access -> SQL Server) ---")
    
    def to_sql_date(val):
        """Converts pandas date/NaT to python date/None."""
        if pd.isna(val):
            return None
        return val.to_pydatetime() if hasattr(val, 'to_pydatetime') else val

    # 1. Extraction from Access
    raw_customers = fetch_from_access("SELECT * FROM Customers")
    raw_employees = fetch_from_access("SELECT * FROM Employees")
    raw_orders = fetch_from_access("SELECT * FROM Orders")
    raw_products = fetch_from_access("SELECT * FROM Products")
    raw_order_details = fetch_from_access("SELECT [Order ID], [Product ID], [Unit Price], Quantity, Discount FROM [Order Details]")
    
    # 2. Transformation
    
    # DimCustomer
    dim_customers = raw_customers.copy()
    dim_customers["CustomerId"] = dim_customers["ID"].astype(str)
    dim_customers["CompanyName"] = dim_customers["Company"]
    dim_customers["ContactName"] = (dim_customers["First Name"].fillna("") + " " + dim_customers["Last Name"].fillna("")).str.strip()
    dim_customers["Address"] = dim_customers["Address"]
    dim_customers["City"] = dim_customers["City"]
    dim_customers["Region"] = dim_customers["State/Province"]
    dim_customers["PostalCode"] = dim_customers["ZIP/Postal Code"]
    dim_customers["Country"] = dim_customers["Country/Region"]
    dim_customers["Phone"] = dim_customers["Business Phone"]
    
    dim_customers = dim_customers[[
        "CustomerId", "CompanyName", "ContactName", "Address", "City", 
        "Region", "PostalCode", "Country", "Phone"
    ]].fillna("Unknown")

    # DimEmployee
    dim_employees = raw_employees.copy()
    dim_employees["EmployeeId"] = dim_employees["ID"].astype(str)
    dim_employees["FirstName"] = dim_employees["First Name"]
    dim_employees["LastName"] = dim_employees["Last Name"]
    dim_employees["Title"] = dim_employees["Job Title"]
    dim_employees["City"] = dim_employees["City"]
    dim_employees["Region"] = dim_employees["State/Province"]
    dim_employees["Country"] = dim_employees["Country/Region"]
    dim_employees["HomePhone"] = dim_employees["Home Phone"]
    # Missing in Access, fill with None for now
    dim_employees["BirthDate"] = None
    dim_employees["HireDate"] = None
    
    dim_employees = dim_employees[[
        "EmployeeId", "FirstName", "LastName", "Title", "BirthDate", 
        "HireDate", "City", "Region", "Country", "HomePhone"
    ]].fillna("Unknown")
    # Restore None for date fields
    dim_employees.loc[dim_employees["BirthDate"] == "Unknown", "BirthDate"] = None
    dim_employees.loc[dim_employees["HireDate"] == "Unknown", "HireDate"] = None

    # DimProduct
    dim_products = raw_products.rename(columns={
        "ID": "ProductId",
        "Product Name": "ProductName",
        "Category": "Category",
        "List Price": "UnitPrice"
    })[["ProductId", "ProductName", "Category", "UnitPrice"]]
    dim_products = dim_products.fillna("Unknown")

    # DimDate
    raw_orders["OrderDate_Parsed"] = pd.to_datetime(raw_orders["Order Date"])
    unique_dates = pd.Series(raw_orders["OrderDate_Parsed"].dropna().unique()).sort_values()
    
    dim_date = pd.DataFrame({"FullDate": unique_dates})
    dim_date["DateId"] = dim_date["FullDate"].dt.strftime("%Y%m%d").astype(int)
    dim_date["Day"] = dim_date["FullDate"].dt.day
    dim_date["Month"] = dim_date["FullDate"].dt.month
    dim_date["MonthName"] = dim_date["FullDate"].dt.strftime("%B")
    dim_date = dim_date.drop_duplicates(subset=["DateId"])

    # FactOrders
    fact_orders = raw_orders.copy()
    fact_orders["OrderId"] = fact_orders["Order ID"].astype(int)
    fact_orders["CustomerId"] = fact_orders["Customer ID"].fillna(-1).astype(int).astype(str) 
    fact_orders["EmployeeId"] = fact_orders["Employee ID"].fillna(-1).astype(int).astype(str)
    fact_orders["DateId"] = fact_orders["OrderDate_Parsed"].apply(
        lambda x: int(x.strftime("%Y%m%d")) if pd.notna(x) else -1
    )
    fact_orders["ShippedDate"] = pd.to_datetime(fact_orders["Shipped Date"]).apply(to_sql_date)
    fact_orders["ShippingFee"] = fact_orders["Shipping Fee"].fillna(0)
    fact_orders["Taxes"] = fact_orders["Taxes"].fillna(0)
    fact_orders["DeliveredFlag"] = fact_orders["Shipped Date"].notna().astype(int)
    
    fact_orders = fact_orders[[
        "OrderId", "CustomerId", "EmployeeId", "DateId", 
        "ShippedDate", "ShippingFee", "Taxes", "DeliveredFlag"
    ]]

    # FactOrderDetails
    fact_order_details = raw_order_details.rename(columns={
        "Order ID": "OrderId",
        "Product ID": "ProductId",
        "Unit Price": "UnitPrice",
        "Quantity": "Quantity",
        "Discount": "Discount"
    })[["OrderId", "ProductId", "UnitPrice", "Quantity", "Discount"]].fillna(0)

    # 3. Data Integrity / Filtering
    valid_custs = set(dim_customers["CustomerId"])
    valid_emps = set(dim_employees["EmployeeId"])
    valid_dates = set(dim_date["DateId"])
    valid_prods = set(dim_products["ProductId"])

    fact_orders = fact_orders[
        fact_orders["CustomerId"].isin(valid_custs) & 
        fact_orders["EmployeeId"].isin(valid_emps) &
        fact_orders["DateId"].isin(valid_dates) &
        (fact_orders["DateId"] != -1)
    ]
    
    fact_order_details = fact_order_details[
        fact_order_details["OrderId"].isin(fact_orders["OrderId"]) &
        fact_order_details["ProductId"].isin(valid_prods)
    ]

    # 4. Loading
    clear_tables()
    load_data(dim_customers, dim_employees, dim_date, dim_products, fact_orders, fact_order_details)

    print("Generating enriched denormalized CSV for visualizations...")
    # Join all data for easy visualization
    # Start with fact_order_details as the base for granular analysis (Revenue per product)
    # Both fact_order_details and dim_products have UnitPrice. We'll use the one from details for Revenue.
    
    # Merge order details with fact orders
    enriched_df = fact_order_details.merge(fact_orders, on="OrderId", how="left")
    
    # Merge with dimensions
    # Standardize Customer columns as primary for visualizations
    enriched_df = enriched_df.merge(dim_customers, on="CustomerId", how="left")
    
    # Use suffix for Employee dimensions to avoid clash with Customer info
    enriched_df = enriched_df.merge(dim_employees, on="EmployeeId", how="left", suffixes=('', '_emp'))
    
    # Merge with products (already handled clashes with suffixes)
    enriched_df = enriched_df.merge(dim_products, on="ProductId", how="left", suffixes=('', '_prod'))
    
    enriched_df = enriched_df.merge(dim_date, on="DateId", how="left")

    # Metrics - Use UnitPrice from fact_order_details
    enriched_df["Revenue"] = enriched_df["UnitPrice"] * enriched_df["Quantity"] * (1 - enriched_df["Discount"])
    
    warehouse_dir = os.path.join(DATA_DIR, "warehouse")
    os.makedirs(warehouse_dir, exist_ok=True)
    csv_path = os.path.join(warehouse_dir, "merged_northwind.csv")
    enriched_df.to_csv(csv_path, index=False)
    print(f"Denormalized data saved to {csv_path}")
    
    print("--- ETL Finished Successfully ---")
