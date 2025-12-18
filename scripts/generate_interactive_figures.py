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
        annotations=[dict(text=f"{len(df)}<br>Orders", x=0.5, y=0.5, font_size=20, showarrow=False, font_color=THEME_COLORS['text'])]
    )
    
    apply_theme(fig)
    html_path = os.path.join(FIGURES_DIR, "delivery_stats_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "delivery_stats.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path} and {png_path}")
    return fig

def create_orders_by_country(df):
    """Create interactive bar chart for orders by country"""
    country_orders = df['Country_x'].value_counts().reset_index().head(10)
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
    print(f"Saved {html_path} and {png_path}")
    return fig

def create_monthly_trend(df):
    """Create interactive area chart for monthly trends"""
    df['YearMonth'] = df['FullDate'].dt.to_period('M').astype(str)
    monthly_orders = df.groupby('YearMonth').size().reset_index(name='OrderCount')
    
    fig = px.area(
        monthly_orders,
        x='YearMonth',
        y='OrderCount',
        title='Monthly Order Growth',
        markers=True
    )
    
    fig.update_traces(
        line=dict(color=THEME_COLORS['primary'], width=3),
        marker=dict(size=6, color=THEME_COLORS['background'], line=dict(width=2, color=THEME_COLORS['primary'])),
        fillcolor='rgba(137, 180, 250, 0.2)'
    )
    
    fig.update_layout(xaxis_title="", yaxis_title="Orders", hovermode='x unified')
    
    apply_theme(fig)
    html_path = os.path.join(FIGURES_DIR, "monthly_trend_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "orders_trend.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path} and {png_path}")
    return fig

def create_3d_scatter(df):
    """Create interactive 3D scatter plot"""
    df['MonthNum'] = df['FullDate'].dt.month
    agg = df.groupby(['MonthNum', 'Country_x']).size().reset_index(name='OrderCount')
    
    fig = px.scatter_3d(
        agg,
        x='MonthNum',
        y='Country_x',
        z='OrderCount',
        color='OrderCount',
        size='OrderCount',
        title='3D Analysis: Seasonality vs Geography',
        color_continuous_scale='Viridis',
        opacity=0.8
    )
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Month'),
            yaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Country'),
            zaxis=dict(backgroundcolor=THEME_COLORS['background'], gridcolor=THEME_COLORS['grid'], title='Volume'),
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        height=800
    )
    
    fig.update_layout(paper_bgcolor=THEME_COLORS['paper'], font_color=THEME_COLORS['text'])
    
    html_path = os.path.join(FIGURES_DIR, "3d_orders_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "3d_orders.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Saved {html_path} and {png_path}")
    return fig

def create_dashboard(df):
    """Create a unified premium dashboard"""
    fig = make_subplots(
        rows=3, cols=2,
        specs=[
            [{'type': 'domain'}, {'type': 'xy'}], 
            [{'type': 'xy', 'colspan': 2}, None], 
            [{'type': 'xy'}, {'type': 'xy'}]     
        ],
        subplot_titles=(
            'Delivery Performance', 'Top Regions', 
            'Global Order Trend', 
            'Top Performing Employees', 'Delivery Efficiency by Country'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.05
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

    country_orders = df['Country_x'].value_counts().head(5).reset_index()
    fig.add_trace(go.Bar(
        x=country_orders['Country_x'], 
        y=country_orders['count'],
        marker=dict(color=country_orders['count'], colorscale='Bluyl'),
        showlegend=False
    ), row=1, col=2)

    df['YearMonth'] = df['FullDate'].dt.to_period('M').astype(str)
    monthly = df.groupby('YearMonth').size().reset_index(name='OrderCount')
    fig.add_trace(go.Scatter(
        x=monthly['YearMonth'], 
        y=monthly['OrderCount'],
        mode='lines', 
        fill='tozeroy',
        line=dict(color=THEME_COLORS['primary'], width=3),
        marker=dict(size=8),
        showlegend=False
    ), row=2, col=1)

    df['EmployeeName'] = df['FirstName'] + ' ' + df['LastName']
    employee_orders = df['EmployeeName'].value_counts().head(5).sort_values(ascending=True).reset_index()
    fig.add_trace(go.Bar(
        y=employee_orders['EmployeeName'], 
        x=employee_orders['count'],
        orientation='h',
        marker=dict(color=THEME_COLORS['warning']),
        showlegend=False
    ), row=3, col=1)

    del_country = df[df['DeliveredFlag'] == 1]['Country_x'].value_counts().head(5).reset_index()
    fig.add_trace(go.Bar(
        x=del_country['Country_x'],
        y=del_country['count'],
        marker=dict(color=THEME_COLORS['accent']),
        showlegend=False
    ), row=3, col=2)

    fig.update_layout(
        height=1200,
        title_text="<b>Northwind Analytics Dashboard</b>",
        title_x=0.5,
        **COMMON_LAYOUT
    )
    fig.update_yaxes(showgrid=False, zeroline=False, row=3, col=1)
    
    html_path = os.path.join(FIGURES_DIR, "dashboard_interactive.html")
    png_path = os.path.join(FIGURES_DIR, "dashboard_interactive.png")
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"Stats: Dashboard generated at {html_path} and {png_path}")
    return fig

def generate_all_figures():
    """Main function to run generation of all figures"""
    print("--- Generating Premium Interactive Figures & PNGs ---")
    try:
        df = load_data()
        create_delivery_stats(df)
        create_orders_by_country(df)
        create_monthly_trend(df)
        create_3d_scatter(df)
        create_dashboard(df)
        print("--- Success ---")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    generate_all_figures()
