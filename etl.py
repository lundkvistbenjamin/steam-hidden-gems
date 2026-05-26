# etl.py
import os
import sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load variables from your local .env file
load_dotenv(override=True)


def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(
            host=os.environ.get("SUPABASE_DB_HOST"),
            database=os.environ.get("SUPABASE_DB_NAME"),
            user=os.environ.get("SUPABASE_DB_USER"),
            password=os.environ.get("SUPABASE_DB_PASSWORD"),
            port=os.environ.get("SUPABASE_DB_PORT")
        )
    except Exception as e:
        # Handle connection failures and terminate if DB is unreachable
        print(f"Database connection initialization failed: {e}")
        sys.exit(1)


def fetch_steamspy_page(page=0):
    """Fetches a batch of game data from the SteamSpy API."""
    url = f"https://steamspy.com/api.php?request=all&page={page}"
    print(f"Requesting payload metadata from SteamSpy Page {page}...")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        print(f"Unexpected status code received: {response.status_code}")
        return None
    except Exception as e:
        # Log network issues without stopping the program entirely
        print(f"Network request exception occurred: {e}")
        return None


def extract_and_load():
    """Orchestrates the extraction, transformation, and database loading process."""
    print("Connecting to database to check processed logs...")
    conn = get_db_connection()

    # Retrieve set of previously processed IDs to prevent redundant inserts
    with conn.cursor() as cur:
        cur.execute("SELECT app_id FROM processed_apps;")
        processed_ids = set(row[0] for row in cur.fetchall())

    print(
        f"Core cache loaded. {len(processed_ids)} entries already processed.")
    print("-" * 50)

    # 1. Fetch data from source
    raw_data = fetch_steamspy_page(page=0)
    if not raw_data:
        print("Pipeline halted. Failed to extract data from upstream source API.")
        conn.close()
        return

    print("Success! Data payload retrieved from API.")
    print("-" * 50)

    games_to_upsert = []
    processed_logs_to_insert = []

    # 2. Transform raw payload
    for app_id_str, metadata in raw_data.items():
        try:
            # Validate app_id format
            app_id = int(app_id_str)
        except ValueError:
            continue

        # Calculate review metrics with safety defaults for missing data
        pos = int(metadata.get('positive', 0))
        neg = int(metadata.get('negative', 0))
        total = pos + neg
        pct = int(round((pos / total) * 100)) if total > 0 else 0

        # Prepare tuple for bulk insertion
        game_record = (
            app_id,
            str(metadata.get('name', 'Unknown Game'))[:255],
            str(metadata.get('developer', 'Unknown'))[:500],
            str(metadata.get('publisher', 'Unknown'))[:500],
            pos,
            neg,
            total,
            pct,
            int(metadata.get('price', 0)),
            int(metadata.get('ccu', 0))
        )
        games_to_upsert.append(game_record)

        # Track only newly discovered app_ids
        if app_id not in processed_ids:
            processed_logs_to_insert.append((app_id,))

    # 3. Load into database
    if games_to_upsert:
        # SQL UPSERT handles existing records by updating them
        upsert_games_query = """
            INSERT INTO games (
                app_id, name, developer, publisher, positive_reviews, 
                negative_reviews, total_reviews, positive_reviews_pct, price_cents, ccu
            ) VALUES %s
            ON CONFLICT (app_id) DO UPDATE SET
                positive_reviews = EXCLUDED.positive_reviews,
                negative_reviews = EXCLUDED.negative_reviews,
                total_reviews = EXCLUDED.total_reviews,
                positive_reviews_pct = EXCLUDED.positive_reviews_pct,
                price_cents = EXCLUDED.price_cents,
                ccu = EXCLUDED.ccu,
                extracted_at = CURRENT_TIMESTAMP;
        """

        # Ledger table to track which apps have been processed
        insert_logs_query = """
            INSERT INTO processed_apps (app_id) VALUES %s
            ON CONFLICT (app_id) DO NOTHING;
        """

        try:
            with conn.cursor() as cur:
                # Efficient bulk execution using execute_values
                print(
                    f"Streaming {len(games_to_upsert)} application records into Supabase...")
                execute_values(cur, upsert_games_query, games_to_upsert)

                if processed_logs_to_insert:
                    print(
                        f"Logging {len(processed_logs_to_insert)} new tracking keys to ledger...")
                    execute_values(cur, insert_logs_query,
                                   processed_logs_to_insert)

                # Finalize database transactions
                conn.commit()
                print(
                    "Success! ETL ingestion round committed and completed successfully.")
        except Exception as e:
            # Revert all changes if any part of the transaction fails
            conn.rollback()
            print(f"Transaction failed. Database state reverted. Error: {e}")
        finally:
            # Ensure database connection is closed regardless of outcome
            conn.close()


if __name__ == "__main__":
    extract_and_load()
