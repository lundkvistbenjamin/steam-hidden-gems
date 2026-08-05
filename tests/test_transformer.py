import pytest
from src.transformers.game_transformer import transform_steamspy_payload

def test_transform_valid_payload():
    """Test standard valid API response payload transformation."""
    raw_data = {
        "730": {
            "name": "Counter-Strike 2",
            "developer": "Valve",
            "publisher": "Valve",
            "positive": 1000,
            "negative": 250,
            "price": 0,
            "ccu": 500000
        }
    }
    processed_ids = set()

    games, logs = transform_steamspy_payload(raw_data, processed_ids)

    assert len(games) == 1
    assert len(logs) == 1
    
    # Assert expected fields in game_record tuple:
    # (app_id, name, developer, publisher, pos, neg, total, pct, price, ccu)
    game = games[0]
    assert game[0] == 730
    assert game[1] == "Counter-Strike 2"
    assert game[2] == "Valve"
    assert game[3] == "Valve"
    assert game[4] == 1000
    assert game[5] == 250
    assert game[6] == 1250  # total reviews
    assert game[7] == 80    # (1000 / 1250) * 100
    assert game[8] == 0
    assert game[9] == 500000
    
    assert logs[0] == (730,)

def test_transform_skips_already_processed_app_ids():
    """Verify that existing App IDs are transformed for stats update but omitted from new log entries."""
    raw_data = {
        "570": {
            "name": "Dota 2",
            "developer": "Valve",
            "publisher": "Valve",
            "positive": 500,
            "negative": 100,
            "price": 0,
            "ccu": 300000
        }
    }
    processed_ids = {570}  # Already in ledger

    games, logs = transform_steamspy_payload(raw_data, processed_ids)

    assert len(games) == 1
    assert len(logs) == 0  # Should NOT generate a new log entry

def test_transform_handles_missing_fields_gracefully():
    """Verify default fallbacks when payload metadata is sparse or missing."""
    raw_data = {
        "10": {}  # Empty metadata dictionary
    }
    processed_ids = set()

    games, logs = transform_steamspy_payload(raw_data, processed_ids)

    assert len(games) == 1
    game = games[0]
    assert game[0] == 10
    assert game[1] == "Unknown Game"
    assert game[2] == "Unknown"
    assert game[3] == "Unknown"
    assert game[4] == 0  # positive reviews
    assert game[5] == 0  # negative reviews
    assert game[6] == 0  # total reviews
    assert game[7] == 0  # review percentage default
    assert game[8] == 0  # price
    assert game[9] == 0  # ccu

def test_transform_string_truncation():
    """Verify oversized strings are truncated to match PostgreSQL column length constraints."""
    raw_data = {
        "100": {
            "name": "A" * 300,        # Exceeds 255 chars
            "developer": "B" * 600,   # Exceeds 500 chars
            "publisher": "C" * 600   # Exceeds 500 chars
        }
    }
    processed_ids = set()

    games, _ = transform_steamspy_payload(raw_data, processed_ids)

    game = games[0]
    assert len(game[1]) == 255
    assert len(game[2]) == 500
    assert len(game[3]) == 500

def test_transform_ignores_invalid_app_ids():
    """Ensure non-integer App ID keys are safely ignored."""
    raw_data = {
        "invalid_id_key": {
            "name": "Broken Record"
        }
    }
    processed_ids = set()

    games, logs = transform_steamspy_payload(raw_data, processed_ids)

    assert len(games) == 0
    assert len(logs) == 0