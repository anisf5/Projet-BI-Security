import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from settings import DATA_DIR, FIGURES_DIR

os.makedirs(FIGURES_DIR, exist_ok=True)


THEME_COLORS = {
    'background': '#1e1e2e', 
    'paper': '#1e1e2e',
    'text': '#cdd6f4',          
    'grid': '#313244',
    'primary': '#89b4fa',       
    'secondary': '#f5c2e7',
    'accent': '#a6e3a1',          
    'warning': '#fab387',          
    'muted': '#6c7086'
}

COMMON_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=14, color=THEME_COLORS['text']),
    plot_bgcolor=THEME_COLORS['background'],
    paper_bgcolor=THEME_COLORS['paper'],
    title_font=dict(size=24, color=THEME_COLORS['primary'], family="Outfit, sans-serif"),
    xaxis=dict(
        showgrid=True, gridcolor=THEME_COLORS['grid'],
        zeroline=False, tickfont=dict(color=THEME_COLORS['muted'])
    ),
    yaxis=dict(
        showgrid=True, gridcolor=THEME_COLORS['grid'],
        zeroline=False, tickfont=dict(color=THEME_COLORS['muted'])
    ),
    margin=dict(l=60, r=40, t=80, b=60),
    hoverlabel=dict(
        bgcolor=THEME_COLORS['background'],
        bordercolor=THEME_COLORS['primary'],
        font=dict(color=THEME_COLORS['text'])
    )
)

def apply_theme(fig):
    fig.update_layout(**COMMON_LAYOUT)
    return fig



def load_data():
    data_path = os.path.join(DATA_DIR, "warehouse", "merged_northwind.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Warehouse data not found at {data_path}")
    df = pd.read_csv(data_path)
    df['FullDate'] = pd.to_datetime(df['FullDate'])
    return df

def create_delivery_stats(df):
    """Create interactive doughnut chart for delivery statistics"""
    delivery_counts = df['DeliveredFlag'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=['Delivered', 'Pending'],
        values=[delivery_counts.get(1, 0), delivery_counts.get(0, 0)],
        hole=0.6,
        marker=dict(colors=[THEME_COLORS['accent'], THEME_COLORS['secondary']]),
        textinfo='percent',
        hoverinfo='label+value',
        textfont=dict(size=16),
        pull=[0.05, 0]
    )])
    
    fig.update_layout(
        title='Order Delivery Status',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=[dict(text=f"{len(df)}<br>Items", x=0.5, y=0.5, font_size=20, showarrow=False, font_color=THEME_COLORS['text'])]
    )
    
    apply_theme(fig)
    html_path = os.path.join(FIGURES_DIR, "delivery_stats_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "delivery_stats.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path}")
    return fig

def create_revenue_by_category(df):
    """Create interactive bar chart for revenue by category"""
    cat_rev = df.groupby('Category')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
    
    fig = px.bar(
        cat_rev,
        x='Category',
        y='Revenue',
        title='Revenue by Product Category',
        color='Revenue',
        color_continuous_scale='Viridis',
        text_auto='.2s'
    )
    
    fig.update_layout(xaxis_title="", yaxis_title="Revenue ($)")
    apply_theme(fig)
    
    html_path = os.path.join(FIGURES_DIR, "revenue_by_category_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "revenue_by_category.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path}")
    return fig

def create_orders_by_country(df):
    """Create interactive bar chart for orders by country"""
    country_orders = df['Country'].value_counts().reset_index().head(10)
    country_orders.columns = ['Country', 'OrderCount']
    
    fig = px.bar(
        country_orders,
        x='Country',
        y='OrderCount',
        title='Top 10 Markets by Order Volume',
        color='OrderCount',
        color_continuous_scale='Bluyl'
    )
    
    fig.update_traces(marker_line_width=0, opacity=0.9)
    fig.update_layout(xaxis_title="", yaxis_title="Orders")
    
    apply_theme(fig)
    html_path = os.path.join(FIGURES_DIR, "orders_by_country_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "orders_by_country.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path}")
    return fig

def create_monthly_trend(df):
    """Create interactive area chart for monthly trends"""
    df['YearMonth'] = df['FullDate'].dt.to_period('M').astype(str)
    monthly_rev = df.groupby('YearMonth')['Revenue'].sum().reset_index()
    
    fig = px.area(
        monthly_rev,
        x='YearMonth',
        y='Revenue',
        title='Monthly Revenue Growth',
        markers=True
    )
    
    fig.update_traces(
        line=dict(color=THEME_COLORS['primary'], width=3),
        marker=dict(size=6, color=THEME_COLORS['background'], line=dict(width=2, color=THEME_COLORS['primary'])),
        fillcolor='rgba(137, 180, 250, 0.2)'
    )
    
    fig.update_layout(xaxis_title="", yaxis_title="Revenue ($)", hovermode='x unified')
    
    apply_theme(fig)
    html_path = os.path.join(FIGURES_DIR, "monthly_trend_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "revenue_trend.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path}")
    return fig

def create_3d_scatter(df):
    """Create interactive 3D scatter plot using Revenue with Year selection"""
    df['Year'] = df['FullDate'].dt.year
    df['MonthNum'] = df['FullDate'].dt.month
    
    # We aggregate by Year, Month, Country for a more detailed view
    agg = df.groupby(['Year', 'MonthNum', 'Country'])['Revenue'].sum().reset_index()
    
    fig = px.scatter_3d(
        agg,
        x='MonthNum',
        y='Country',
        z='Revenue',
        color='Year',
        size='Revenue',
        title='3D Analysis: Revenue Seasonality vs Geography',
        color_continuous_scale='Viridis',
        opacity=0.8,
        labels={'MonthNum': 'Month', 'Revenue': 'Revenue ($)'}
    )
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Month'),
            yaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Country'),
            zaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Revenue'),
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        height=800
    )
    
    fig.update_layout(paper_bgcolor=THEME_COLORS['paper'], font_color=THEME_COLORS['text'])
    
    html_path = os.path.join(FIGURES_DIR, "3d_orders_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "3d_orders.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path}")
    return fig

def create_employee_performance_3d(df):
    """Create a 3D scatter plot of Employee performance across years"""
    df['Year'] = df['FullDate'].dt.year
    df['EmployeeName'] = df['FirstName'].astype(str) + ' ' + df['LastName'].astype(str)
    
    emp_year_rev = df.groupby(['EmployeeName', 'Year'])['Revenue'].sum().reset_index()
    
    fig = px.scatter_3d(
        emp_year_rev,
        x='EmployeeName',
        y='Year',
        z='Revenue',
        color='Revenue',
        size='Revenue',
        title='3D Analysis: Employee Performance vs Year vs Revenue',
        color_continuous_scale='Plasma',
        opacity=0.9,
        labels={'Revenue': 'Total Revenue ($)'}
    )
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Employee'),
            yaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Year'),
            zaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Revenue'),
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        height=800
    )
    
    fig.update_layout(paper_bgcolor=THEME_COLORS['paper'], font_color=THEME_COLORS['text'])
    
    html_path = os.path.join(FIGURES_DIR, "employee_3d_performance_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "employee_3d_performance.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path}")
    return fig

def create_employee_explorer(df):
    """Create a Plotly figure with a dropdown for employees showing their revenue over time."""
    df['EmployeeName'] = df['FirstName'].astype(str) + ' ' + df['LastName'].astype(str)
    employees = sorted(df['EmployeeName'].unique())
    
    fig = go.Figure()

    for emp in employees:
        emp_df = df[df['EmployeeName'] == emp].copy()
        emp_df['YearMonth'] = emp_df['FullDate'].dt.to_period('M').astype(str)
        monthly = emp_df.groupby('YearMonth')['Revenue'].sum().reset_index()
        
        fig.add_trace(go.Bar(
            x=monthly['YearMonth'],
            y=monthly['Revenue'],
            name=emp,
            visible=(emp == employees[0]),
            marker_color=THEME_COLORS['primary']
        ))

    dropdown_buttons = [
        dict(
            method="update",
            label=emp,
            args=[{"visible": [emp == e for e in employees]},
                  {"title": f"Revenue Trend: {emp}"}]
        ) for emp in employees
    ]

    fig.update_layout(
        updatemenus=[dict(
            active=0, 
            buttons=dropdown_buttons, 
            x=0, y=1.15, 
            xanchor='left', yanchor='top',
            bgcolor=THEME_COLORS['background'],
            font=dict(color=THEME_COLORS['text'])
        )],
        title=f"Revenue Trend: {employees[0]}",
        xaxis_title="Month",
        yaxis_title="Revenue ($)"
    )
    
    apply_theme(fig)
    html_path = os.path.join(FIGURES_DIR, "employee_explorer_interactive.html")
    fig.write_html(html_path)
    print(f"Saved {html_path}")
    return fig

def create_dashboard(df):
    """Create a unified premium dashboard with Revenue focus"""
    fig = make_subplots(
        rows=3, cols=2,
        specs=[
            [{'type': 'domain'}, {'type': 'xy'}], 
            [{'type': 'xy', 'colspan': 2}, None], 
            [{'type': 'xy'}, {'type': 'xy'}]     
        ],
        subplot_titles=(
            'Delivery Performance', 'Revenue by Category', 
            'Global Revenue Trend', 
            'Top Countries by Revenue', 'Revenue by Employee'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    delivery_counts = df['DeliveredFlag'].value_counts()
    fig.add_trace(go.Pie(
        labels=['Delivered', 'Pending'],
        values=[delivery_counts.get(1, 0), delivery_counts.get(0, 0)],
        hole=0.6,
        marker=dict(colors=[THEME_COLORS['accent'], THEME_COLORS['secondary']]),
        textinfo='percent',
        showlegend=False
    ), row=1, col=1)

    cat_rev = df.groupby('Category')['Revenue'].sum().head(5).reset_index()
    fig.add_trace(go.Bar(
        x=cat_rev['Category'], 
        y=cat_rev['Revenue'],
        marker=dict(color=cat_rev['Revenue'], colorscale='Viridis'),
        showlegend=False
    ), row=1, col=2)

    df['YearMonth'] = df['FullDate'].dt.to_period('M').astype(str)
    monthly = df.groupby('YearMonth')['Revenue'].sum().reset_index()
    fig.add_trace(go.Scatter(
        x=monthly['YearMonth'], 
        y=monthly['Revenue'],
        mode='lines', 
        fill='tozeroy',
        line=dict(color=THEME_COLORS['primary'], width=3),
        marker=dict(size=8),
        showlegend=False
    ), row=2, col=1)

    country_rev = df.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(5).sort_values().reset_index()
    fig.add_trace(go.Bar(
        y=country_rev['Country'], 
        x=country_rev['Revenue'],
        orientation='h',
        marker=dict(color=THEME_COLORS['warning']),
        showlegend=False
    ), row=3, col=1)

    emp_rev = df.groupby('FirstName')['Revenue'].sum().sort_values(ascending=False).head(5).reset_index()
    fig.add_trace(go.Bar(
        x=emp_rev['FirstName'],
        y=emp_rev['Revenue'],
        marker=dict(color=THEME_COLORS['accent']),
        showlegend=False
    ), row=3, col=2)

    fig.update_layout(
        height=1200,
        title_text="<b>Northwind Strategic Business Dashboard</b>",
        title_x=0.5,
        **COMMON_LAYOUT
    )
    
    html_path = os.path.join(FIGURES_DIR, "dashboard_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "dashboard_interactive.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Stats: Dashboard generated at {html_path}")
    return fig

def generate_all_figures():
    """Main function to run generation of all figures"""
    print("--- Generating Premium Interactive Figures & PNGs ---")
    try:
        df = load_data()
        create_delivery_stats(df)
        create_revenue_by_category(df)
        create_orders_by_country(df)
        create_monthly_trend(df)
        create_3d_scatter(df)
        create_employee_explorer(df)
        create_employee_performance_3d(df)
        create_dashboard(df)
        print("--- Success ---")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    generate_all_figures()
