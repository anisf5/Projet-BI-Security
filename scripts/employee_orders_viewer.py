# scripts/employee_orders_viewer.py
import sys
import pandas as pd
from data_helpers import get_employees, get_employee_orders

def main():
    print("--- Northwind Employee Orders Viewer ---")
    try:
        employees = get_employees()
        
        if employees.empty:
            print("No employees found in the Access database.")
            return

        print("\nAvailable Employees:")
        print("-" * 30)
        # Using to_string for better alignment in CLI
        print(employees.to_string(index=False, header=["ID", "Full Name"]))
        print("-" * 30)

        while True:
            emp_id_input = input("\nEnter Employee ID to view orders (or 'q' to quit): ").strip()
            
            if emp_id_input.lower() == 'q':
                print("Exiting...")
                break
            
            if not emp_id_input.isdigit():
                print("Invalid input. Please enter a numerical Employee ID.")
                continue
            
            emp_id = int(emp_id_input)
            
            # Check if emp_id exists in employees list
            if emp_id not in employees['ID'].values:
                print(f"Employee ID {emp_id} not found.")
                continue

            orders = get_employee_orders(emp_id)

            if orders.empty:
                print(f"\nNo orders found for Employee ID {emp_id}.")
            else:
                print(f"\nOrders for Employee ID {emp_id}:")
                print("=" * 60)
                # Filter out some rows if too many? No, let's show all for now.
                print(orders.to_string(index=False))
                print("=" * 60)
                print(f"Total Oders: {len(orders)}")
                
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
