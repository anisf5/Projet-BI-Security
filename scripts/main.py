
from database_manager import setup_sql_server
from etl_pipeline import run_etl_pipeline

def main():
    try:
        setup_sql_server()
        run_etl_pipeline()
    except Exception as e:
        print(f"\n[FATAL ERROR] Pipeline failed: {e}")

if __name__ == "__main__":
    main()
