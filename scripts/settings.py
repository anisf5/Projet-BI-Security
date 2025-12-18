
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
ACCESS_DB_PATH = os.path.join(DATA_DIR, "Northwind 2012.accdb")

SQL_SERVER = r"WIN-4DQD0F0RTQ8\SQLANIS"
SQL_DATABASE = "Global_Northwind"
SQL_DRIVER = "SQL Server"

ACCESS_DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"
