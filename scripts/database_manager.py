# database_manager.py
import pyodbc
from settings import SQL_SERVER, SQL_DATABASE, SQL_DRIVER

def get_sql_conn_str(db="master"):
    return f"DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};DATABASE={db};Trusted_Connection=yes;"

def setup_sql_server():
    """Ensures SQL Server DB and Schema exist."""
    print("--- Setting up SQL Server ---")
    

    try:
        conn = pyodbc.connect(get_sql_conn_str("master"), autocommit=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sys.databases WHERE name = ?", SQL_DATABASE)
        if not cur.fetchone():
            print(f"Creating Database: {SQL_DATABASE}")
            cur.execute(f"CREATE DATABASE {SQL_DATABASE}")
        else:
            print(f"Database {SQL_DATABASE} exists.")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Master DB connection failed: {e}")
        raise

 
    try:
        conn = pyodbc.connect(get_sql_conn_str(SQL_DATABASE), autocommit=True)
        cur = conn.cursor()
        
        tables = {
            "DimCustomer": """
                CustomerId NVARCHAR(50) PRIMARY KEY,
                CompanyName NVARCHAR(255),
                City NVARCHAR(100),
                Country NVARCHAR(100)
            """,
            "DimEmployee": """
                EmployeeId NVARCHAR(50) PRIMARY KEY,
                FirstName NVARCHAR(100),
                LastName NVARCHAR(100),
                City NVARCHAR(100),
                Country NVARCHAR(100)
            """,
            "DimDate": """
                DateId INT PRIMARY KEY,
                FullDate DATE,
                Day INT,
                Month INT,
                MonthName NVARCHAR(20)
            """,
            "FactOrders": """
                OrderId INT PRIMARY KEY,
                CustomerId NVARCHAR(50),
                EmployeeId NVARCHAR(50),
                DateId INT,
                DeliveredFlag INT,
                FOREIGN KEY (CustomerId) REFERENCES DimCustomer(CustomerId),
                FOREIGN KEY (EmployeeId) REFERENCES DimEmployee(EmployeeId),
                FOREIGN KEY (DateId) REFERENCES DimDate(DateId)
            """
        }

        for table, schema in tables.items():
            check_sql = f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table}' AND xtype='U') CREATE TABLE {table} ({schema})"
            cur.execute(check_sql)
        
        print("Schema verified.")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Schema setup failed: {e}")
        raise

def clear_tables():
    """Truncates tables before load."""
    conn = pyodbc.connect(get_sql_conn_str(SQL_DATABASE), autocommit=True)
    cur = conn.cursor()
   
    for t in ["FactOrders", "DimDate", "DimEmployee", "DimCustomer"]:
        try:
            cur.execute(f"DELETE FROM {t}")
        except:
            pass
    conn.close()
    print("Target tables cleared.")

def load_data(dim_customers, dim_employees, dim_date, fact_orders):
    """Inserts DataFrames into SQL Server."""
    conn = pyodbc.connect(get_sql_conn_str(SQL_DATABASE))
    cur = conn.cursor()

    print(f"Loading {len(dim_customers)} Customers...")
    for _, r in dim_customers.iterrows():
        cur.execute("INSERT INTO DimCustomer (CustomerId, CompanyName, City, Country) VALUES (?, ?, ?, ?)",
                    str(r["CustomerId"]), r["CompanyName"], r["City"], r["Country"])

    print(f"Loading {len(dim_employees)} Employees...")
    for _, r in dim_employees.iterrows():
        cur.execute("INSERT INTO DimEmployee (EmployeeId, FirstName, LastName, City, Country) VALUES (?, ?, ?, ?, ?)",
                    str(r["EmployeeId"]), r["FirstName"], r["LastName"], r["City"], r["Country"])

    print(f"Loading {len(dim_date)} Dates...")
    for _, r in dim_date.iterrows():
        cur.execute("INSERT INTO DimDate (DateId, FullDate, Day, Month, MonthName) VALUES (?, ?, ?, ?, ?)",
                    int(r["DateId"]), r["FullDate"].to_pydatetime(), r["Day"], r["Month"], r["MonthName"])

    print(f"Loading {len(fact_orders)} Orders...")
    for _, r in fact_orders.iterrows():
        cur.execute("INSERT INTO FactOrders (OrderId, CustomerId, EmployeeId, DateId, DeliveredFlag) VALUES (?, ?, ?, ?, ?)",
                    int(r["OrderId"]), str(r["CustomerId"]), str(r["EmployeeId"]), r["DateId"], r["DeliveredFlag"])

    conn.commit()
    conn.close()
