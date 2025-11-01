from services.api_service import fetch_smartwatch_data
from services.db_service import insert_health_data
from utils.data_formatter import format_health_data

def main():
    print("⏳ Fetching data from smartwatch API...")
    raw_data = fetch_smartwatch_data()

    if not raw_data:
        print("❌ No data fetched from API.")
        return

    # If the API returns a list of records
    if isinstance(raw_data, list):
        formatted = [format_health_data(item) for item in raw_data]
    else:
        formatted = format_health_data(raw_data)

    print("🧹 Data formatted successfully!")

    # Insert into MongoDB
    insert_health_data(formatted)

if __name__ == "__main__":
    main()
