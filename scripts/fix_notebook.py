import json
import os
import pandas as pd

NOTEBOOK_PATH = "notebooks/visualization_interactive.ipynb"
DATA_PATH = "data/warehouse/merged_northwind.csv"

def fix_notebook():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Notebook not found: {NOTEBOOK_PATH}")
        return

    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # 1. Start with a fresh set of cells to ensure clean structure
    # We'll keep the first 3 cells (Title, Install, Imports) and then rebuild
    # cell 0: Title
    # cell 1: %pip install
    # cell 2: imports
    # cell 3: Data loading (we'll standardize this)
    
    new_cells = []
    new_cells.append(nb['cells'][0]) # Title
    new_cells.append(nb['cells'][1]) # Install
    new_cells.append(nb['cells'][2]) # Imports
    
    # Standardized Load Cell
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Load the definitive denormalized dataset\n",
            "import os\n",
            "import pandas as pd\n",
            "import plotly.express as px\n",
            "import plotly.graph_objects as go\n",
            "\n",
            "data_path = \"../data/warehouse/merged_northwind.csv\"\n",
            "if not os.path.exists(data_path):\n",
            "    print(f\"File not found: {data_path}. Please run 'python scripts/main.py' first.\")\n",
            "    df = pd.DataFrame() # Empty fallback\n",
            "else:\n",
            "    df = pd.read_csv(data_path)\n",
            "    df['FullDate'] = pd.to_datetime(df['FullDate'])\n",
            "    # Clean data for Sunburst (drop rows with missing hierarchy keys)\n",
            "    df = df.dropna(subset=['Category', 'ProductName'])\n",
            "    print(\"Data loaded and cleaned successfully.\")\n",
            "    print(f\"Total records available: {len(df)}\")\n",
            "    display(df.head())"
        ]
    })

    # Define the sections we want
    sections = [
        {
            "title": "0. Executive KPI Summary",
            "source": [
                "total_revenue = df['Revenue'].sum()\n",
                "total_orders = df['OrderId'].nunique()\n",
                "avg_order_value = total_revenue / total_orders if total_orders > 0 else 0\n",
                "\n",
                "print(f\"Total Revenue: ${total_revenue:,.2f}\")\n",
                "print(f\"Total Orders: {total_orders}\")\n",
                "print(f\"Average Order Value: ${avg_order_value:,.2f}\")"
            ]
        },
        {
            "title": "1. Revenue Breakdown (Sunburst)",
            "source": [
                "fig_sunburst = px.sunburst(\n",
                "    df, \n",
                "    path=['Category', 'ProductName'], \n",
                "    values='Revenue', \n",
                "    color='Revenue', \n",
                "    color_continuous_scale='Viridis',\n",
                "    title='Product Revenue Composition'\n",
                ")\n",
                "fig_sunburst.update_layout(height=700, template='plotly_dark')\n",
                "fig_sunburst.show()"
            ]
        },
        {
            "title": "2. Monthly Revenue Trend",
            "source": [
                "df['YearMonth'] = df['FullDate'].dt.to_period('M').astype(str)\n",
                "monthly_rev = df.groupby('YearMonth')['Revenue'].sum().reset_index()\n",
                "\n",
                "fig_trend = px.line(\n",
                "    monthly_rev, \n",
                "    x='YearMonth', \n",
                "    y='Revenue', \n",
                "    title='Monthly Revenue Trajectory',\n",
                "    markers=True,\n",
                "    template='plotly_dark'\n",
                ")\n",
                "fig_trend.update_traces(line_color='#89b4fa', line_width=3)\n",
                "fig_trend.show()"
            ]
        },
        {
            "title": "3. Global Revenue by Country",
            "source": [
                "country_rev = df.groupby('Country')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)\n",
                "fig_country = px.bar(\n",
                "    country_rev, \n",
                "    x='Country', \n",
                "    y='Revenue', \n",
                "    color='Revenue', \n",
                "    title='Top Markets by Revenue',\n",
                "    template='plotly_dark'\n",
                ")\n",
                "fig_country.show()"
            ]
        },
        {
            "title": "4. Delivery Performance Overview",
            "source": [
                "df['DeliveryStatus'] = df['DeliveredFlag'].map({1: 'Delivered', 0: 'Not Delivered'})\n",
                "status_counts = df['DeliveryStatus'].value_counts().reset_index()\n",
                "status_counts.columns = ['Status', 'Count']\n",
                "\n",
                "fig_pie = px.pie(\n",
                "    status_counts, \n",
                "    values='Count', \n",
                "    names='Status', \n",
                "    hole=0.4,\n",
                "    title='Order Fulfillment Status',\n",
                "    color='Status',\n",
                "    color_discrete_map={'Delivered': '#2ecc71', 'Not Delivered': '#e74c3c'},\n",
                "    template='plotly_dark'\n",
                ")\n",
                "fig_pie.show()"
            ]
        },
        {
            "title": "5. Interactive Employee Explorer",
            "source": [
                "import ipywidgets as widgets\n",
                "from IPython.display import display\n",
                "\n",
                "df['EmployeeName'] = df['FirstName'].astype(str) + ' ' + df['LastName'].astype(str)\n",
                "employees = sorted(df['EmployeeName'].unique())\n",
                "\n",
                "dropdown = widgets.Dropdown(\n",
                "    options=employees,\n",
                "    description='Employee:',\n",
                "    style={'description_width': 'initial'}\n",
                ")\n",
                "\n",
                "out = widgets.Output()\n",
                "\n",
                "def update_chart(change):\n",
                "    emp_name = change['new']\n",
                "    with out:\n",
                "        out.clear_output()\n",
                "        emp_df = df[df['EmployeeName'] == emp_name]\n",
                "        fig = px.bar(\n",
                "            emp_df.groupby('Category')['Revenue'].sum().reset_index(),\n",
                "            x='Category', y='Revenue', \n",
                "            title=f\"Revenue Contribution by {emp_name}\",\n",
                "            color='Revenue', template='plotly_dark'\n",
                "        )\n",
                "        fig.show()\n",
                "\n",
                "dropdown.observe(update_chart, names='value')\n",
                "display(dropdown, out)\n",
                "if employees: update_chart({'new': employees[0]})"
            ]
        },
        {
            "title": "6. 3D Order Landscape",
            "source": [
                "fig_3d = px.scatter_3d(\n",
                "    df,\n",
                "    x='Country',\n",
                "    y='FullDate',\n",
                "    z='Revenue',\n",
                "    color='DeliveryStatus',\n",
                "    hover_data=['OrderId', 'ProductName'],\n",
                "    title='Strategic Order Landscape: Country vs Date vs Revenue',\n",
                "    template='plotly_dark',\n",
                "    height=800\n",
                ")\n",
                "fig_3d.update_layout(margin=dict(l=0, r=0, b=0, t=40))\n",
                "fig_3d.show()"
            ]
        }
    ]

    for sec in sections:
        new_cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"## {sec['title']}\n"]
        })
        new_cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + ("\n" if not line.endswith("\n") else "") for line in sec['source']]
        })

    nb['cells'] = new_cells
    
    # Save with no outputs for a clean slate
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None

    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Successfully fixed and re-organized {NOTEBOOK_PATH}")

if __name__ == "__main__":
    fix_notebook()
