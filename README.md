# Steam Hidden Gems ETL Pipeline

**Live Demo:** https://gemengine.vercel.app/

**Full-Stack App Repository:** https://github.com/lundkvistbenjamin/steam-hidden-gems-app

A lightweight ETL pipeline that extracts Steam game metadata from the SteamSpy API, transforms and validates incoming records, and synchronizes them with a PostgreSQL database hosted on Supabase. Built with Python, the project emphasizes efficient batch processing, transactional reliability, and clean database synchronization for analytics applications.

## Core Features

### Automated SteamSpy Data Extraction

The pipeline connects directly to the SteamSpy public API to retrieve batches of Steam application metadata. Network requests include timeout protection and graceful exception handling, allowing the process to fail safely without corrupting downstream operations.

### Data Transformation & Validation

Incoming payloads are normalized before loading into PostgreSQL. The transformation layer validates application IDs, calculates total review counts and positive review percentages, applies safe defaults for missing fields, and truncates oversized strings to match database constraints.

### High-Performance Batch Loading

Rather than executing thousands of individual INSERT statements, the pipeline performs bulk UPSERT operations using PostgreSQL's `ON CONFLICT` clause together with `psycopg2.execute_values`.

This dramatically reduces database round trips while keeping game statistics synchronized with the latest SteamSpy data.

### Incremental Processing Ledger

A dedicated `processed_apps` table tracks every application that has already been discovered.

Existing games continue receiving updated statistics while newly discovered App IDs are logged automatically, preventing duplicate tracking records.

## Tech Stack

### Runtime

- Python 3.11

### Database

- Supabase PostgreSQL

### Libraries & Tools

- `requests` — SteamSpy API communication
- `psycopg2-binary` — PostgreSQL driver
- `python-dotenv` — Environment variable management
- `pytest` — Unit testing framework

### Infrastructure

- GitHub Actions (scheduled execution)
- SteamSpy Public API
- Supabase PostgreSQL

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── pipeline.yml         # GitHub Actions workflow for scheduled ETL runs
├── .vscode/
│   └── settings.json            # VS Code configuration settings
├── src/
│   ├── db/
│   │   ├── connection.py        # Database connection pool & context managers
│   │   └── repository.py        # SQL queries and bulk database interaction logic
│   ├── extractors/
│   │   └── steamspy.py          # SteamSpy API client and network extraction
│   ├── transformers/
│   │   └── game_transformer.py  # Data payload cleaning, normalization, and mapping
│   ├── config.py                # Environment variable loading and global configurations
│   └── pipeline.py              # Main ETL pipeline orchestrator module
├── tests/
│   └── test_transformer.py      # Unit tests for data transformation logic
├── .gitignore
├── LICENSE
├── README.md
├── requirements-dev.txt         # Development & testing dependencies (pytest)
├── requirements.txt             # Core production dependencies
└── test_connection.py           # Database and API connectivity verification script
```

## ETL Workflow

The pipeline follows a structured extraction, transformation, and loading workflow:

### 1. Data Extraction

Retrieve Steam application metadata in batches from the SteamSpy API with network timeout handling and failure protection.

### 2. Data Transformation

Normalize incoming records by validating application IDs, calculating derived metrics, applying defaults for missing values, and ensuring compatibility with database constraints.

### 3. Data Loading

Perform bulk UPSERT operations into PostgreSQL using transactional queries to efficiently synchronize game information.

## Reliability & Data Integrity

The pipeline is designed around transactional consistency.

Every execution loads processed IDs into memory, prepares transformed records, performs bulk UPSERT operations, and commits the transaction only after every query succeeds.

If any database operation fails, the transaction is rolled back automatically, ensuring partial updates never reach the database.

## Security

Database credentials are never stored in source code.

Configuration is provided through environment variables, making the project suitable for deployment with GitHub Actions secrets, Supabase, or other CI/CD platforms.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
