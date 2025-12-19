import json
import os

NOTEBOOK_PATH = "notebooks/visualization_interactive.ipynb"

def enrich_notebook():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Notebook not found: {NOTEBOOK_PATH}")
        return

    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Define new cells
    new_cells = []

    # 1. Executive Summary Markdown
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 0. Executive Revenue Summary\n",
            "Key performance indicators (KPIs) showing the overall health of the business."
        ]
    })

    # 2. Executive Summary Code
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "total_revenue = df['Revenue'].sum()\n",
            "total_orders = df['OrderId'].nunique()\n",
            "avg_order_value = total_revenue / total_orders if total_orders > 0 else 0\n",
            "\n",
            "print(f\"Total Revenue: ${total_revenue:,.2f}\")\n",
            "print(f\"Total Orders: {total_orders}\")\n",
            "print(f\"Average Order Value: ${avg_order_value:,.2f}\")"
        ]
    })

    # 3. Revenue by Category Sunburst Markdown
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Revenue Composition (Sunburst)\n",
            "Drill down into product categories and individual products to see revenue contributions."
        ]
    })

    # 4. Revenue by Category Sunburst Code
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig_sunburst = px.sunburst(\n",
            "    df, \n",
            "    path=['Category', 'ProductName'], \n",
            "    values='Revenue', \n",
            "    color='Revenue', \n",
            "    color_continuous_scale='Viridis',\n",
            "    title='Revenue Breakdown by Category and Product'\n",
            ")\n",
            "fig_sunburst.update_layout(height=700)\n",
            "fig_sunburst.show()"
        ]
    })

    # Insert new cells at appropriate positions
    # We'll insert the summary at the beginning (after imports/data loading)
    # Data loading is usually cell index 3
    nb['cells'].insert(4, new_cells[0])
    nb['cells'].insert(5, new_cells[1])
    
    # Add others at the end for now
    nb['cells'].extend(new_cells[2:])

    # Update existing cells to use correct column names
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell.get('source', []))
            # Fix Country_x -> Country
            if 'Country_x' in source:
                source = source.replace('Country_x', 'Country')
                cell['source'] = [source]
            # Fix DeliveredFlag references if needed (it should still be same)

    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Successfully enriched {NOTEBOOK_PATH}")

if __name__ == "__main__":
    enrich_notebook()
