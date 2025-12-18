
import pandas as pd
import pyodbc
from settings import SQL_SERVER, SQL_DATABASE, DATA_DIR, FIGURES_DIR
import os

def get_connection():
    conn_str = f"DRIVER={{SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)

def generate_olap_report():
    print("--- Starting OLAP Cube Analysis ---")
    conn = get_connection()
    
 
    print("Fetching and Denormalizing Data...")
    query = """
    SELECT 
        f.OrderId,
        d.DateId,
        d.FullDate,
        d.Year_ as OrderYear,  -- Need to handle if Year_ column exists or extract it
        d.MonthName,
        c.Country as CustomerCountry,
        c.City as CustomerCity,
        e.FirstName as EmpFirstName,
        e.LastName as EmpLastName,
        f.DeliveredFlag
    FROM FactOrders f
    LEFT JOIN DimDate d ON f.DateId = d.DateId
    LEFT JOIN DimCustomer c ON f.CustomerId = c.CustomerId
    LEFT JOIN DimEmployee e ON f.EmployeeId = e.EmployeeId
    """

    query_safe = """
    SELECT 
        f.OrderId,
        d.FullDate,
        c.Country as CustomerCountry,
        c.City as CustomerCity,
        e.FirstName as EmpFirstName,
        f.DeliveredFlag
    FROM FactOrders f
    LEFT JOIN DimDate d ON f.DateId = d.DateId
    LEFT JOIN DimCustomer c ON f.CustomerId = c.CustomerId
    LEFT JOIN DimEmployee e ON f.EmployeeId = e.EmployeeId
    """
    
    df = pd.read_sql(query_safe, conn)
    conn.close()
    

    df["FullDate"] = pd.to_datetime(df["FullDate"])
    df["Year"] = df["FullDate"].dt.year
    df["Quarter"] = df["FullDate"].dt.quarter
    df["Month"] = df["FullDate"].dt.month_name()
    
    print(f"Base Cube Loaded: {len(df)} records.")

    rollup_year_country = df.groupby(["Year", "CustomerCountry"]).size().reset_index(name="TotalOrders")
    print("OLAP Operation: Roll-up (Year, Country) done.")

    slice_usa = df[df["CustomerCountry"] == "USA"].copy()
    print(f"OLAP Operation: Slice (Country='USA') done. Records: {len(slice_usa)}")


    dice_usa_uk_2006 = df[
        (df["CustomerCountry"].isin(["USA", "UK"])) & 
        (df["Year"] == 2006)
    ].copy()
    print(f"OLAP Operation: Dice (USA/UK & 2006) done. Records: {len(dice_usa_uk_2006)}")

    pivot_emp_country = pd.crosstab(df["EmpFirstName"], df["CustomerCountry"], margins=True)
    print("OLAP Operation: Pivot (Employee vs Country) done.")

    output_path = os.path.join(FIGURES_DIR, "OLAP_Report.xlsx")
    print(f"Exporting to {output_path}...")
    
    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Base_Cube_Raw", index=False)
            rollup_year_country.to_excel(writer, sheet_name="Rollup_Year_Country", index=False)
            slice_usa.to_excel(writer, sheet_name="Slice_USA", index=False)
            dice_usa_uk_2006.to_excel(writer, sheet_name="Dice_USA_UK_2006", index=False)
            pivot_emp_country.to_excel(writer, sheet_name="Pivot_Emp_Country")
        print("Report generated successfully.")
    except Exception as e:
        print(f"Failed to write Excel: {e}")

if __name__ == "__main__":
    generate_olap_report()
