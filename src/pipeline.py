from src.db.connection import get_db_connection
from src.db.repository import fetch_processed_app_ids, save_etl_batch
from src.extractors.steamspy import fetch_steamspy_page
from src.transformers.game_transformer import transform_steamspy_payload

def extract_and_load(page=0):
    """Orchestrates the extraction, transformation, and database loading process."""
    print("Connecting to database to check processed logs...")
    
    # 1. Fetch data from source
    raw_data = fetch_steamspy_page(page=page)
    if not raw_data:
        print("Pipeline halted. Failed to extract data from upstream source API.")
        return

    print("Success! Data payload retrieved from API.")
    print("-" * 50)

    try:
        with get_db_connection() as conn:
            processed_ids = fetch_processed_app_ids(conn)
            print(f"Core cache loaded. {len(processed_ids)} entries already processed.")
            print("-" * 50)

            # Transform raw payload
            games_to_upsert, processed_logs_to_insert = transform_steamspy_payload(
                raw_data, processed_ids
            )

            # 3. Load into database
            if games_to_upsert:
                save_etl_batch(conn, games_to_upsert, processed_logs_to_insert)
    except Exception as e:
        # Errors handled by connection context manager and repository
        pass

if __name__ == "__main__":
    extract_and_load()