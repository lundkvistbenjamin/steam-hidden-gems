# Nightly SteamSpy Batch ETL Pipeline

A data ingestion pipeline engineered to extract application payloads from SteamSpy, transform metadata matrices, and execute highly efficient batch operations against a PostgreSQL instance hosted on Supabase.

## Overview

The ETL architecture manages database synchronization by:
* Fetching comprehensive catalog dumps from the SteamSpy API sequentially
* Recalculating dynamic user engagement parameters and formatting pricing structures
* Utilizing atomic transaction queries to perform mass upserts into production tables
* Retaining a relational ledger to monitor historical tracking status

## Features

### Extraction and Network Fault Tolerance
* Automated network handling featuring strict request timeouts
* Graceful degradation protocols ensuring localized exceptions do not halt cascading routines
* Integrated connectivity test scripts to map schema states across remote database environments

### Transformation and Validation Mechanics
* String manipulation to prevent system truncation by capping data fields at size boundaries
* Mathematical data normalizing that updates user review ratings automatically
* Type verification routines that drop corruption anomalies before they enter storage arrays

### Loading Optimization
* Mass ingestion powered by batch processing queries
* High-performance transaction execution using native driver array utilities
* Atomic commit and rollback design to protect data integrity against transport loss

## System Architecture

The project operates across a decoupled three-tier architecture:

1. **Extraction (SteamSpy API Data Target):** Connects to the public endpoint matrix to capture raw batch updates on concurrent traffic metrics and overall user voting logs.
2. **Transformation (Python Engine Core):** Processes the raw payload dictionary, calculates positive approval trends, matches IDs, and organizes records into clean tabular formats.
3. **Loading Layer (Supabase PostgreSQL):** Forwards ready collections using custom queries to run relational updates instantly.

## Technical Details

### Transaction Processing Strategy
The engine utilizes a distinct dual-query strategy within a shared context loop to update active listings while tracking newly discovered records independently. It handles active metric updates via conflict resolution mechanics while simultaneously appending new tracking keys directly to an isolated system table.

### Dependencies and Tech Stack
* **Runtime Environment:** Python 3.11
* **Data Transport Layer:** `requests`
* **Database Driver Extension:** `psycopg2-binary` (PostgreSQL client)
* **Configuration Context:** `python-dotenv`
* **Workflow Automation Engine:** GitHub Actions (Ubuntu Environment runner core)

## Output Interpretation

* **Core Cache Verification:** Scans the upstream server schema to report how many items are currently tracked by the system ledger.
* **Payload Stream Confirmation:** Validates standard server responses to guarantee tracking channels remain open.
* **Database Target Feed:** Reports bulk upload progress transparently as data streams into the PostgreSQL tables.

## Limitations

* Hard-coded to process the default dashboard view index of the external provider API page targets.
* Subject to upstream payload size variations and regional server latency timeouts.
* Requires complete target database schema fields to be established prior to execution.

## Security Note

Database authentication strings must be stored securely inside external repository engine systems. Connection configurations should be passed at runtime using encrypted context injections managed through automated runner properties.

## License

MIT License - see [LICENSE](LICENSE) file for details.
