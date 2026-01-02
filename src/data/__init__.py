"""
Data module for Kings Shot Chart Generator.

This module provides functions for loading, validating, and
processing shot data from various sources (CSV, NBA API).
"""

from src.data.data_loader import (
    load_shots_csv,
    filter_shots,
    get_shot_summary,
    validate_columns,
    convert_dtypes,
    DataValidationError,
    MissingColumnsError,
    InvalidDataTypeError,
    REQUIRED_COLUMNS,
    COLUMN_DTYPES,
)

from src.data.nba_api_client import (
    NBAApiClient,
    NBAApiError,
    PlayerNotFoundError,
    GameNotFoundError,
    RateLimitError,
)

__all__ = [
    # Data loader
    "load_shots_csv",
    "filter_shots",
    "get_shot_summary",
    "validate_columns",
    "convert_dtypes",
    "DataValidationError",
    "MissingColumnsError",
    "InvalidDataTypeError",
    "REQUIRED_COLUMNS",
    "COLUMN_DTYPES",
    # NBA API client
    "NBAApiClient",
    "NBAApiError",
    "PlayerNotFoundError",
    "GameNotFoundError",
    "RateLimitError",
]
