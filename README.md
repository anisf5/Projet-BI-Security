# ING3 Security Project

## Project Structure
- `/data`: Contains all source Excel files (`Orders.xlsx`, etc.).
- `/scripts`: Contains the ETL (`script.py`) and Dashboard (`dashboard.py`) scripts.
- `/figures`: Contains generated charts (`orders_by_country.png`, etc.).
- `/reports`: Contains the assignment PDF.
- `/notebooks`: Placeholder for Jupyter notebooks.
- `/video`: Placeholder for the presentation video.

## Setup
1. Install Python dependencies:
   ```bash
   pip install pandas pyodbc openpyxl matplotlib seaborn
   ```
2. Ensure SQL Server is running and accessible at `WIN-4DQD0F0RTQ8\SQLANIS`.

## Execution

### ETL Process
To load data from Excel to SQL Server:
```bash
python scripts/script.py
```
This will create the `Global_Northwind` database (if missing) and populate the tables.

### Dashboard
To generate visualization figures:
```bash
python scripts/dashboard.py
```
Check the `/figures` directory for the output images.
