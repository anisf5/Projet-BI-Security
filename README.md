# Projet-BI-Security

A small BI project that extracts, transforms and visualizes a Northwind dataset with scripts, notebooks and generated interactive figures.

**Highlights**
- ETL pipeline to extract data from the Access database and generated CSVs.
- Scripts to populate a local data warehouse and create OLAP-ready outputs.
- Static and interactive visualizations (HTML) in `figures/`.

**Quick Links**
- Data: `data/` (includes `Northwind 2012.accdb`, extracted CSVs and `warehouse/` merged CSV)
- Scripts: `scripts/` (ETL, DB manager, figure generation, OLAP cube)
- Figures: `figures/` (interactive and static visualizations)
- Notebooks: `notebooks/` (analysis and visualization notebooks)

Project structure (selected)
- `data/`
   - `Northwind 2012.accdb` — original Access DB
   - `extracted/` — intermediate CSV extracts (Customers, Orders, Products, etc.)
   - `warehouse/merged_northwind.csv` — merged warehouse-ready CSV
- `scripts/`
   - `etl_pipeline.py` — main ETL orchestration
   - `database_manager.py` — helpers to create/load DB tables
   - `data_helpers.py` — parsing and cleaning utilities
   - `generate_figures.py` and `generate_interactive_figures.py` — figure generation
   - `olap_cube.py` — cube/aggregation helpers
   - `dashboard.py` / `main.py` — entry points for reporting or demo runs

Requirements
- Python 3.8+ recommended
- Typical Python libraries used: `pandas`, `numpy`, `sqlalchemy`/`pyodbc`, `openpyxl`, `matplotlib`, `seaborn`, `plotly` (for interactive HTMLs)

Install common deps (example):
```powershell
pip install pandas numpy sqlalchemy pyodbc openpyxl matplotlib seaborn plotly
pip install -r requirements.txt
```

Configuration
- Connection strings and environment-specific settings live in `scripts/settings.py`. Edit that file to point to your database (SQL Server, SQLite, or other supported backends).

Quickstart
1. Prepare data: either use `data/Northwind 2012.accdb` or the CSVs under `data/extracted/`.
2. Run the ETL to build the warehouse/merged CSV or populate a local DB:
```powershell
python scripts/etl_pipeline.py
```
3. Generate figures (static and interactive):
```powershell
python scripts/generate_figures.py
python scripts/generate_interactive_figures.py
```
4. Open generated HTML visualizations from `figures/` in a browser.

Notebooks
- See `notebooks/visualization.ipynb` and `notebooks/visualization_interactive.ipynb` for exploratory analysis and examples.

Notes & Troubleshooting
- If you need to read the Access DB (`*.accdb`) on Windows, ensure an appropriate ODBC driver or `pyodbc` setup is available.

- If you prefer not to use a DB, `scripts/etl_pipeline.py` can be adapted to produce `warehouse/merged_northwind.csv` which downstream scripts consume.

