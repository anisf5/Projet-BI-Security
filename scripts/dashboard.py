
import os
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from olap_cube import generate_olap_report

from settings import SQL_SERVER, SQL_DATABASE, FIGURES_DIR

if not os.path.exists(FIGURES_DIR):
    os.makedirs(FIGURES_DIR)


sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#1e1e2e", "figure.facecolor": "#1e1e2e", "grid.color": "#313244", "text.color": "#cdd6f4", "xtick.color": "#cdd6f4", "ytick.color": "#cdd6f4", "axes.labelcolor": "#cdd6f4", "axes.titlecolor": "#cdd6f4"})
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'

def get_connection():
    from settings import SQL_DRIVER
    conn_str = f"DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)

def generate_charts():
    try:
        conn = get_connection()
    except Exception as e:
        print(f"[WARN] Could not connect to SQL Server: {e}. Skipping static chart generation.")
        return
    
    print("Generating: Revenue by Country...")
    query = """
    SELECT c.Country, SUM(fd.UnitPrice * fd.Quantity * (1 - fd.Discount)) as TotalRevenue 
    FROM FactOrderDetails fd
    JOIN FactOrders f ON fd.OrderId = f.OrderId
    JOIN DimCustomer c ON f.CustomerId = c.CustomerId 
    GROUP BY c.Country 
    HAVING SUM(fd.UnitPrice * fd.Quantity * (1 - fd.Discount)) > 0
    ORDER BY TotalRevenue DESC
    """
    df = pd.read_sql(query, conn)
    
    plt.figure()
    ax = sns.barplot(data=df.head(10), x="TotalRevenue", y="Country", palette="viridis", hue="Country", legend=False)
    ax.set_title("Top 10 Markets by Revenue", fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel("Revenue ($)", fontsize=12)
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/orders_by_country.png")
    plt.close()

    print("Generating: Revenue Trend...")
    query = """
    SELECT FullDate, SUM(fd.UnitPrice * fd.Quantity * (1 - fd.Discount)) as DailyRevenue 
    FROM FactOrderDetails fd
    JOIN FactOrders f ON fd.OrderId = f.OrderId
    JOIN DimDate d ON f.DateId = d.DateId 
    WHERE FullDate IS NOT NULL 
    GROUP BY FullDate 
    ORDER BY FullDate
    """
    df = pd.read_sql(query, conn)
    
    plt.figure()
    sns.lineplot(data=df, x="FullDate", y="DailyRevenue", color="#89b4fa", linewidth=3)
    plt.fill_between(df["FullDate"], df["DailyRevenue"], color="#89b4fa", alpha=0.2)
    
    plt.title("Daily Revenue Performance", fontsize=20, fontweight='bold', pad=20)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Revenue ($)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/orders_trend.png")
    plt.close()

    print("Generating: Employee Revenue Performance...")
    query = """
    SELECT e.FirstName, SUM(fd.UnitPrice * fd.Quantity * (1 - fd.Discount)) as Revenue 
    FROM FactOrderDetails fd
    JOIN FactOrders f ON fd.OrderId = f.OrderId
    JOIN DimEmployee e ON f.EmployeeId = e.EmployeeId 
    GROUP BY e.FirstName 
    ORDER BY Revenue DESC
    """
    df = pd.read_sql(query, conn)
    
    plt.figure()
    sns.barplot(data=df, x="FirstName", y="Revenue", palette="flare", hue="FirstName", legend=False)
    plt.title("Employee Revenue Generation", fontsize=20, fontweight='bold', pad=20)
    plt.xlabel("Employee")
    plt.ylabel("Total Revenue ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/employee_performance.png")
    plt.close()
    
    conn.close()

def generate_html_report():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Northwind Executive B.I. Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
            body { font-family: 'Outfit', sans-serif; background: #11111b; color: #cdd6f4; margin: 0; padding: 40px; }
            header { text-align: center; margin-bottom: 60px; }
            h1 { color: #89b4fa; font-size: 3em; margin-bottom: 10px; }
            p.subtitle { color: #a6adc8; font-size: 1.2em; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 30px; max-width: 1600px; margin: 0 auto; }
            .card { background: #1e1e2e; padding: 20px; border-radius: 16px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); transition: transform 0.2s; }
            .card:hover { transform: translateY(-5px); }
            img { width: 100%; height: auto; border-radius: 8px; }
            .btn-container { text-align: center; margin: 40px 0; }
            .btn { background: #89b4fa; color: #1e1e2e; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; transition: all 0.3s; }
            .btn:hover { background: #b4befe; box-shadow: 0 0 20px rgba(137, 180, 250, 0.5); }
            .footer { text-align: center; margin-top: 80px; color: #585b70; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <header>
            <h1>Northwind Executive Analytics</h1>
            <p class="subtitle">Real-time Revenue and Operational Performance</p>
        </header>

        <div class="btn-container">
            <a href="dashboard_interactive.html" class="btn">Launch Strategic Dashboard ✨</a>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Revenue by Market</h3>
                <img src="orders_by_country.png" alt="Revenue by Country">
            </div>
            <div class="card">
                <h3>Product Category Insights</h3>
                <img src="revenue_by_category.png" alt="Revenue by Category">
            </div>
            <div class="card">
                <h3>Sales Performance</h3>
                <img src="employee_performance.png" alt="Employee Revenue">
            </div>
            <div class="card">
                <h3>Interactive Explorer</h3>
                <p style="text-align: center; margin-top: 50px;">
                    <a href="employee_explorer_interactive.html" class="btn">Open Employee Drilldown 🔍</a>
                </p>
            </div>
            <div class="card">
                <h3>3D Revenue Landscape</h3>
                <img src="3d_orders.png" alt="3D Revenue View">
            </div>
            <div class="card">
                <h3>Financial Growth</h3>
                <img src="revenue_trend.png" alt="Revenue Trend">
            </div>
        </div>
        <div class="footer">
            <p>Generated by Northwind BI Pipeline (Enriched Schema)</p>
        </div>
    </body>
    </html>
    """
    with open(f"{FIGURES_DIR}/index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print(f"Strategic Dashboard generated at: {os.path.abspath(f'{FIGURES_DIR}/index.html')}")

from generate_interactive_figures import generate_all_figures

if __name__ == "__main__":
  
    generate_all_figures()
    generate_charts()
    generate_html_report()
    generate_olap_report()
