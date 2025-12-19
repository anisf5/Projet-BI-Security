
import pandas as pd
import pyodbc
from settings import SQL_SERVER, SQL_DATABASE, DATA_DIR, FIGURES_DIR
import os

def get_connection():
    from settings import SQL_DRIVER
    conn_str = f"DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)

def generate_olap_report():
    print("--- Starting OLAP Cube Analysis ---")
    conn = get_connection()
    
    print("Fetching and Denormalizing Data from SQL Server...")
    query = """
    SELECT 
        fd.OrderId,
        fo.CustomerId,
        fo.EmployeeId,
        p.ProductName,
        p.Category,
        dp.FullDate,
        c.Country as CustomerCountry,
        c.City as CustomerCity,
        e.FirstName + ' ' + e.LastName as EmployeeName,
        fd.UnitPrice,
        fd.Quantity,
        fd.Discount,
        (fd.UnitPrice * fd.Quantity * (1 - fd.Discount)) as Revenue,
        fo.DeliveredFlag
    FROM FactOrderDetails fd
    JOIN FactOrders fo ON fd.OrderId = fo.OrderId
    JOIN DimProduct p ON fd.ProductId = p.ProductId
    JOIN DimCustomer c ON fo.CustomerId = c.CustomerId
    JOIN DimEmployee e ON fo.EmployeeId = e.EmployeeId
    LEFT JOIN DimDate dp ON fo.DateId = dp.DateId
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    df["FullDate"] = pd.to_datetime(df["FullDate"])
    df["Year"] = df["FullDate"].dt.year
    df["Month"] = df["FullDate"].dt.month_name()
    
    print(f"Base Cube Loaded: {len(df)} records.")

    # Roll-up: Revenue by Year and Country
    rollup_revenue = df.groupby(["Year", "CustomerCountry"])["Revenue"].sum().reset_index()
    print("OLAP Operation: Roll-up (Revenue by Year, Country) done.")

    # Slice: Orders for a specific category, e.g., 'Beverages'
    slice_beverages = df[df["Category"] == "Beverages"].copy()
    print(f"OLAP Operation: Slice (Category='Beverages') done.")

    # Dice: Revenue in 2006 for top countries
    dice_2006_top = df[
        (df["Year"] == 2006) & 
        (df["CustomerCountry"].isin(["USA", "UK", "France", "Germany"]))
    ].copy()
    print("OLAP Operation: Dice (2006 & Top Countries) done.")

    # Pivot: Revenue by Category vs Country
    pivot_revenue = pd.pivot_table(df, values="Revenue", index="Category", columns="CustomerCountry", aggfunc="sum", fill_value=0)
    print("OLAP Operation: Pivot (Revenue by Category vs Country) done.")

    output_path = os.path.join(FIGURES_DIR, "OLAP_Report.xlsx")
    print(f"Exporting to {output_path}...")
    
    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Base_Cube_Raw", index=False)
            rollup_revenue.to_excel(writer, sheet_name="Revenue_Year_Country", index=False)
            slice_beverages.to_excel(writer, sheet_name="Slice_Beverages", index=False)
            dice_2006_top.to_excel(writer, sheet_name="Dice_2006_Top", index=False)
            pivot_revenue.to_excel(writer, sheet_name="Pivot_Category_Country")
        print("Report generated successfully.")
    except Exception as e:
        print(f"Failed to write Excel: {e}")

if __name__ == "__main__":
    generate_olap_report()
