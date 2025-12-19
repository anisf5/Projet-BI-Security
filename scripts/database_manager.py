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
                ContactName NVARCHAR(255),
                Address NVARCHAR(255),
                City NVARCHAR(100),
                Region NVARCHAR(100),
                PostalCode NVARCHAR(50),
                Country NVARCHAR(100),
                Phone NVARCHAR(50)
            """,
            "DimEmployee": """
                EmployeeId NVARCHAR(50) PRIMARY KEY,
                FirstName NVARCHAR(100),
                LastName NVARCHAR(100),
                Title NVARCHAR(100),
                BirthDate DATETIME2,
                HireDate DATETIME2,
                City NVARCHAR(100),
                Region NVARCHAR(100),
                Country NVARCHAR(100),
                HomePhone NVARCHAR(50)
            """,
            "DimProduct": """
                ProductId INT PRIMARY KEY,
                ProductName NVARCHAR(255),
                Category NVARCHAR(100),
                UnitPrice MONEY
            """,
            "DimDate": """
                DateId INT PRIMARY KEY,
                FullDate DATETIME2,
                Day INT,
                Month INT,
                MonthName NVARCHAR(20)
            """,
            "FactOrders": """
                OrderId INT PRIMARY KEY,
                CustomerId NVARCHAR(50),
                EmployeeId NVARCHAR(50),
                DateId INT,
                ShippedDate DATETIME2,
                ShippingFee MONEY,
                Taxes MONEY,
                DeliveredFlag INT,
                FOREIGN KEY (CustomerId) REFERENCES DimCustomer(CustomerId),
                FOREIGN KEY (EmployeeId) REFERENCES DimEmployee(EmployeeId),
                FOREIGN KEY (DateId) REFERENCES DimDate(DateId)
            """,
            "FactOrderDetails": """
                DetailId INT IDENTITY(1,1) PRIMARY KEY,
                OrderId INT,
                ProductId INT,
                UnitPrice MONEY,
                Quantity INT,
                Discount FLOAT,
                FOREIGN KEY (OrderId) REFERENCES FactOrders(OrderId),
                FOREIGN KEY (ProductId) REFERENCES DimProduct(ProductId)
            """
        }

        # Drop tables in reverse order of dependencies if schema needs refresh
        # (For simplicity here, we only CREATE IF NOT EXISTS, but user might want a full refresh)
        # To handle schema changes, we might need to drop them. 
        # But let's stick to the current logic of CREATE IF NOT EXISTS.
        # Actually, since we are adding columns, we should probably DROP them if they exist and we want to change schema.
        # Let's add a DROP logic for a clean sync.
        
        for table in reversed(list(tables.keys())):
            cur.execute(f"IF EXISTS (SELECT * FROM sysobjects WHERE name='{table}' AND xtype='U') DROP TABLE {table}")

        for table, schema in tables.items():
            print(f"Creating Table: {table}")
            cur.execute(f"CREATE TABLE {table} ({schema})")
        
        print("Schema verified and updated.")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Schema setup failed: {e}")
        raise

def clear_tables():
    """Truncates tables before load."""
    conn = pyodbc.connect(get_sql_conn_str(SQL_DATABASE), autocommit=True)
    cur = conn.cursor()
   
    for t in ["FactOrderDetails", "FactOrders", "DimDate", "DimEmployee", "DimCustomer", "DimProduct"]:
        try:
            cur.execute(f"DELETE FROM {t}")
        except:
            pass
    conn.close()
    print("Target tables cleared.")

def load_data(dim_customers, dim_employees, dim_date, dim_products, fact_orders, fact_order_details):
    """Inserts DataFrames into SQL Server."""
    conn = pyodbc.connect(get_sql_conn_str(SQL_DATABASE))
    cur = conn.cursor()

    print(f"Loading {len(dim_customers)} Customers...")
    for _, r in dim_customers.iterrows():
        cur.execute("INSERT INTO DimCustomer (CustomerId, CompanyName, ContactName, Address, City, Region, PostalCode, Country, Phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    str(r["CustomerId"]), r["CompanyName"], r.get("ContactName"), r.get("Address"), r["City"], r.get("Region"), r.get("PostalCode"), r["Country"], r.get("Phone"))

    print(f"Loading {len(dim_employees)} Employees...")
    for _, r in dim_employees.iterrows():
        cur.execute("INSERT INTO DimEmployee (EmployeeId, FirstName, LastName, Title, BirthDate, HireDate, City, Region, Country, HomePhone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    str(r["EmployeeId"]), r["FirstName"], r["LastName"], r.get("Title"), r.get("BirthDate"), r.get("HireDate"), r["City"], r.get("Region"), r["Country"], r.get("HomePhone"))

    print(f"Loading {len(dim_products)} Products...")
    for _, r in dim_products.iterrows():
        cur.execute("INSERT INTO DimProduct (ProductId, ProductName, Category, UnitPrice) VALUES (?, ?, ?, ?)",
                    int(r["ProductId"]), r["ProductName"], r.get("Category"), r.get("UnitPrice"))

    print(f"Loading {len(dim_date)} Dates...")
    for _, r in dim_date.iterrows():
        cur.execute("INSERT INTO DimDate (DateId, FullDate, Day, Month, MonthName) VALUES (?, ?, ?, ?, ?)",
                    int(r["DateId"]), r["FullDate"].to_pydatetime(), r["Day"], r["Month"], r["MonthName"])

    print(f"Loading {len(fact_orders)} Orders...")
    for _, r in fact_orders.iterrows():
        try:
            cur.execute("INSERT INTO FactOrders (OrderId, CustomerId, EmployeeId, DateId, ShippedDate, ShippingFee, Taxes, DeliveredFlag) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        int(r["OrderId"]), str(r["CustomerId"]), str(r["EmployeeId"]), r["DateId"], r.get("ShippedDate"), r.get("ShippingFee"), r.get("Taxes"), r["DeliveredFlag"])
        except Exception as e:
            print(f"[ERROR] Failed to load Order {r.get('OrderId')}: {e}")
            print(f"Row data: {r.to_dict()}")
            raise

    print(f"Loading {len(fact_order_details)} Order Details...")
    for _, r in fact_order_details.iterrows():
        cur.execute("INSERT INTO FactOrderDetails (OrderId, ProductId, UnitPrice, Quantity, Discount) VALUES (?, ?, ?, ?, ?)",
                    int(r["OrderId"]), int(r["ProductId"]), r["UnitPrice"], r["Quantity"], r["Discount"])

    conn.commit()
    conn.close()
