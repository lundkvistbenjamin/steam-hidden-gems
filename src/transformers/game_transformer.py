from typing import Dict, Any, Tuple, List

def transform_steamspy_payload(
    raw_data: Dict[str, Any], 
    processed_ids: set
) -> Tuple[List[Tuple], List[Tuple]]:
    """Transforms raw API payload into database-ready records and log entries."""
    games_to_upsert = []
    processed_logs_to_insert = []

    # 2. Transform raw payload
    for app_id_str, metadata in raw_data.items():
        try:
            # Validate app_id format
            app_id = int(app_id_str)
        except (ValueError, TypeError):
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

    return games_to_upsert, processed_logs_to_insert