import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.cm as cm
import numpy as np
from settings import DATA_DIR, FIGURES_DIR

os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data():
    data_path = os.path.join(DATA_DIR, "warehouse", "merged_northwind.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Warehouse data not found at {data_path}")
    df = pd.read_csv(data_path)
    df['FullDate'] = pd.to_datetime(df['FullDate'])
    return df

def plot_orders_by_country(df):
    plt.figure(figsize=(12, 6))
    country_orders = df['Country_x'].value_counts().reset_index()
    country_orders.columns = ['Country', 'OrderCount']
    sns.barplot(data=country_orders, x='Country', y='OrderCount', palette='viridis')
    plt.title('Total Orders by Country')
    plt.xticks(rotation=45)
    plt.tight_layout()
    save_path = os.path.join(FIGURES_DIR, "orders_by_country.png")
    plt.savefig(save_path)
    print(f"Saved {save_path}")
    plt.close()

def plot_orders_by_employee(df):
    plt.figure(figsize=(12, 6))
    df['EmployeeName'] = df['FirstName'] + ' ' + df['LastName']
    employee_orders = df['EmployeeName'].value_counts().reset_index()
    employee_orders.columns = ['EmployeeName', 'OrderCount']
    sns.barplot(data=employee_orders, x='OrderCount', y='EmployeeName', palette='magma')
    plt.title('Orders by Employee')
    plt.xlabel('Number of Orders')
    plt.ylabel('Employee')
    plt.tight_layout()
    save_path = os.path.join(FIGURES_DIR, "orders_by_employee.png")
    plt.savefig(save_path)
    print(f"Saved {save_path}")
    plt.close()

def plot_monthly_trend(df):
    plt.figure(figsize=(12, 6))
    df['YearMonth'] = df['FullDate'].dt.to_period('M')
    monthly_orders = df.groupby('YearMonth').size().reset_index(name='OrderCount')
    monthly_orders['YearMonth'] = monthly_orders['YearMonth'].astype(str)
    sns.lineplot(data=monthly_orders, x='YearMonth', y='OrderCount', marker='o')
    plt.title('Monthly Orders Trend')
    plt.xticks(rotation=45)
    plt.xlabel('Month')
    plt.ylabel('Number of Orders')
    plt.tight_layout()
    save_path = os.path.join(FIGURES_DIR, "monthly_orders_trend.png")
    plt.savefig(save_path)
    print(f"Saved {save_path}")
    plt.close()

def plot_3d_orders(df):
    """
    3D Scatter Plot: 
    X = Month (numeric)
    Y = Country (mapped to numeric)
    Z = Order Count
    """
    from mpl_toolkits.mplot3d import Axes3D
    

    df['MonthNum'] = df['FullDate'].dt.month

    agg = df.groupby(['MonthNum', 'Country_x']).size().reset_index(name='OrderCount')

    countries = agg['Country_x'].unique()
    country_map = {c: i for i, c in enumerate(countries)}
    agg['CountryId'] = agg['Country_x'].map(country_map)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    p = ax.scatter(
        agg['MonthNum'], 
        agg['CountryId'], 
        agg['OrderCount'], 
        c=agg['OrderCount'], 
        cmap='coolwarm', 
        s=100,
        depthshade=True
    )
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Country')
    ax.set_zlabel('Order Count')
    ax.set_title('3D View: Orders by Month and Country')

    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries)
    
    fig.colorbar(p, ax=ax, shrink=0.5, aspect=5, label='Order Count')
    
    save_path = os.path.join(FIGURES_DIR, "3d_orders_by_month_country.png")
    plt.savefig(save_path)
    print(f"Saved {save_path}")
    plt.close()

if __name__ == "__main__":
    print("--- Generating Figures ---")
    try:
        df = load_data()
        plot_orders_by_country(df)
        plot_orders_by_employee(df)
        plot_monthly_trend(df)
        plot_3d_orders(df)
        print("--- Figures Generated Successfully ---")
    except Exception as e:
        print(f"[ERROR] Failed to generate figures: {e}")
