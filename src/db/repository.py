import logging
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

# SQL UPSERT handles existing records by updating them
UPSERT_GAMES_QUERY = """
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
INSERT_LOGS_QUERY = """
    INSERT INTO processed_apps (app_id) VALUES %s
    ON CONFLICT (app_id) DO NOTHING;
"""

def fetch_processed_app_ids(conn) -> set:
    # Retrieve set of previously processed IDs to prevent redundant inserts
    with conn.cursor() as cur:
        cur.execute("SELECT app_id FROM processed_apps;")
        return set(row[0] for row in cur.fetchall())

def save_etl_batch(conn, games_to_upsert: list, processed_logs_to_insert: list):
    with conn.cursor() as cur:
        if games_to_upsert:
            # Efficient bulk execution using execute_values
            print(f"Streaming {len(games_to_upsert)} application records into Supabase...")
            execute_values(cur, UPSERT_GAMES_QUERY, games_to_upsert)

        if processed_logs_to_insert:
            print(f"Logging {len(processed_logs_to_insert)} new tracking keys to ledger...")
            execute_values(cur, INSERT_LOGS_QUERY, processed_logs_to_insert)

        # Finalize database transactions
        conn.commit()
        print("Success! ETL ingestion round committed and completed successfully.")