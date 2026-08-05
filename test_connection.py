import os
import requests
import psycopg2
from dotenv import load_dotenv

# Load variables from your local .env file
load_dotenv(override=True)

# 1. Test Outbound API Route
print("Testing connectivity to SteamSpy API...")
try:
    response = requests.get(
        "https://steamspy.com/api.php?request=all&page=0", timeout=10)
    print(
        f"Success! SteamSpy answered with status code: {response.status_code}")
except Exception as e:
    print(f"Failed to reach SteamSpy: {e}")

print("-" * 50)

# 2. Test Supabase Database Route
print("Testing connection to Supabase PostgreSQL...")
try:
    conn = psycopg2.connect(
        host=os.environ.get("SUPABASE_DB_HOST"),
        database=os.environ.get("SUPABASE_DB_NAME"),
        user=os.environ.get("SUPABASE_DB_USER"),
        port=os.environ.get("SUPABASE_DB_PORT"),
        password=os.environ.get("SUPABASE_DB_PASSWORD")
    )
    print("Success! Database authenticated and session established.")

    # Run a quick query to verify our newly created tables exist
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Found tables in public schema: {tables}")

    conn.close()
except Exception as e:
    print(f"Failed to connect to Supabase: {e}")