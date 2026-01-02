"""
Data Loader Module for Kings Shot Chart Generator.

This module provides functions to load shot data from CSV files,
validate the data structure, and return properly typed DataFrames.

Example:
    >>> from src.data.data_loader import load_shots_csv
    >>> df = load_shots_csv('data/sample_shots.csv')
    >>> print(df.head())
"""

from pathlib import Path
from typing import Optional, Union, List

import pandas as pd
import numpy as np


# Required columns for shot data (based on project-spec.md section 4.1)
REQUIRED_COLUMNS = [
    'game_id',
    'player_id',
    'player_name',
    'team',
    'period',
    'minutes_remaining',
    'seconds_remaining',
    'shot_made',
    'shot_type',
    'shot_distance',
    'loc_x',
    'loc_y',
    'shot_zone',
    'action_type',
]

# Data type specifications for each column
COLUMN_DTYPES = {
    'game_id': str,
    'player_id': 'Int64',  # Nullable integer
    'player_name': str,
    'team': str,
    'period': 'Int64',
    'minutes_remaining': 'Int64',
    'seconds_remaining': 'Int64',
    'shot_made': bool,
    'shot_type': str,
    'shot_distance': float,
    'loc_x': float,
    'loc_y': float,
    'shot_zone': str,
    'action_type': str,
}


class DataValidationError(Exception):
    """Raised when shot data fails validation."""
    pass


class MissingColumnsError(DataValidationError):
    """Raised when required columns are missing from the data."""

    def __init__(self, missing_columns: List[str]):
        self.missing_columns = missing_columns
        msg = f"Missing required columns: {', '.join(missing_columns)}"
        super().__init__(msg)


class InvalidDataTypeError(DataValidationError):
    """Raised when a column has invalid data types."""

    def __init__(self, column: str, expected_type: str, error_detail: str):
        self.column = column
        self.expected_type = expected_type
        msg = f"Column '{column}' should be {expected_type}: {error_detail}"
        super().__init__(msg)


def validate_columns(df: pd.DataFrame) -> None:
    """
    Validate that all required columns are present in the DataFrame.

    Args:
        df: DataFrame to validate.

    Raises:
        MissingColumnsError: If any required columns are missing.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise MissingColumnsError(missing)


def convert_shot_made(value: Union[str, bool, int, float]) -> Optional[bool]:
    """
    Convert shot_made values to boolean.

    Handles various representations:
    - Boolean: True/False
    - String: 'True'/'False', '1'/'0', 'yes'/'no', 'made'/'missed'
    - Numeric: 1/0

    Args:
        value: The value to convert.

    Returns:
        Boolean value or None if missing.
    """
    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ('true', '1', 'yes', 'made', 'y'):
            return True
        elif value_lower in ('false', '0', 'no', 'missed', 'n'):
            return False

    raise ValueError(f"Cannot convert '{value}' to boolean")


def convert_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame columns to their proper data types.

    Args:
        df: DataFrame with raw data.

    Returns:
        DataFrame with corrected data types.

    Raises:
        InvalidDataTypeError: If conversion fails for a column.
    """
    df = df.copy()

    # Convert game_id to string (handle numeric game IDs)
    try:
        df['game_id'] = df['game_id'].astype(str)
    except Exception as e:
        raise InvalidDataTypeError('game_id', 'string', str(e))

    # Convert player_id to nullable integer
    try:
        df['player_id'] = pd.to_numeric(df['player_id'], errors='coerce').astype('Int64')
    except Exception as e:
        raise InvalidDataTypeError('player_id', 'integer', str(e))

    # Convert string columns
    for col in ['player_name', 'team', 'shot_type', 'shot_zone', 'action_type']:
        try:
            df[col] = df[col].astype(str).replace('nan', pd.NA)
        except Exception as e:
            raise InvalidDataTypeError(col, 'string', str(e))

    # Convert period and time columns to nullable integers
    for col in ['period', 'minutes_remaining', 'seconds_remaining']:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        except Exception as e:
            raise InvalidDataTypeError(col, 'integer', str(e))

    # Convert shot_made to boolean
    try:
        df['shot_made'] = df['shot_made'].apply(convert_shot_made)
    except Exception as e:
        raise InvalidDataTypeError('shot_made', 'boolean', str(e))

    # Convert numeric columns to float
    for col in ['shot_distance', 'loc_x', 'loc_y']:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
        except Exception as e:
            raise InvalidDataTypeError(col, 'float', str(e))

    return df


def validate_data_ranges(df: pd.DataFrame, strict: bool = False) -> List[str]:
    """
    Validate that data values are within expected ranges.

    Args:
        df: DataFrame to validate.
        strict: If True, raise exception on warnings. Default False.

    Returns:
        List of warning messages for out-of-range values.

    Raises:
        DataValidationError: If strict=True and validation fails.
    """
    warnings = []

    # Check period range (1-4 for regulation, 5+ for OT)
    if df['period'].notna().any():
        invalid_periods = df[(df['period'] < 1) | (df['period'] > 10)]
        if len(invalid_periods) > 0:
            warnings.append(f"Found {len(invalid_periods)} shots with unusual period values")

    # Check minutes_remaining range (0-12 for most periods)
    if df['minutes_remaining'].notna().any():
        invalid_mins = df[(df['minutes_remaining'] < 0) | (df['minutes_remaining'] > 12)]
        if len(invalid_mins) > 0:
            warnings.append(f"Found {len(invalid_mins)} shots with minutes outside 0-12 range")

    # Check seconds_remaining range (0-59)
    if df['seconds_remaining'].notna().any():
        invalid_secs = df[(df['seconds_remaining'] < 0) | (df['seconds_remaining'] > 59)]
        if len(invalid_secs) > 0:
            warnings.append(f"Found {len(invalid_secs)} shots with seconds outside 0-59 range")

    # Check shot_distance (reasonable range 0-50 feet)
    if df['shot_distance'].notna().any():
        invalid_dist = df[(df['shot_distance'] < 0) | (df['shot_distance'] > 50)]
        if len(invalid_dist) > 0:
            warnings.append(f"Found {len(invalid_dist)} shots with distance outside 0-50 feet")

    # Check loc_x range (NBA API: -250 to 250)
    if df['loc_x'].notna().any():
        invalid_x = df[(df['loc_x'] < -300) | (df['loc_x'] > 300)]
        if len(invalid_x) > 0:
            warnings.append(f"Found {len(invalid_x)} shots with loc_x outside court bounds")

    # Check loc_y range (NBA API: typically -50 to 420)
    if df['loc_y'].notna().any():
        invalid_y = df[(df['loc_y'] < -100) | (df['loc_y'] > 500)]
        if len(invalid_y) > 0:
            warnings.append(f"Found {len(invalid_y)} shots with loc_y outside court bounds")

    if strict and warnings:
        raise DataValidationError("Data validation warnings:\n" + "\n".join(warnings))

    return warnings


def load_shots_csv(
    filepath: Union[str, Path],
    validate: bool = True,
    strict: bool = False,
) -> pd.DataFrame:
    """
    Load shot data from a CSV file.

    Reads a CSV file containing shot data, validates the structure,
    and converts columns to appropriate data types.

    Args:
        filepath: Path to the CSV file.
        validate: If True, validate column structure. Default True.
        strict: If True, raise exceptions on data range warnings. Default False.

    Returns:
        DataFrame with shot data and proper data types.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        MissingColumnsError: If required columns are missing.
        InvalidDataTypeError: If data type conversion fails.
        DataValidationError: If strict=True and validation fails.

    Example:
        >>> df = load_shots_csv('data/sample_shots.csv')
        >>> print(f"Loaded {len(df)} shots")
        >>> print(df.dtypes)
    """
    filepath = Path(filepath)

    # Check file exists
    if not filepath.exists():
        raise FileNotFoundError(f"Shot data file not found: {filepath}")

    # Check file extension
    if filepath.suffix.lower() != '.csv':
        raise ValueError(f"Expected CSV file, got: {filepath.suffix}")

    # Load CSV
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise DataValidationError(f"Failed to read CSV file: {e}")

    # Check for empty file
    if len(df) == 0:
        raise DataValidationError("CSV file is empty (no data rows)")

    # Validate columns
    if validate:
        validate_columns(df)
        # Convert data types (only if validation passed)
        df = convert_dtypes(df)
        # Validate data ranges
        warnings = validate_data_ranges(df, strict=strict)
        if warnings and not strict:
            for warning in warnings:
                print(f"Warning: {warning}")

    return df


def get_shot_summary(df: pd.DataFrame) -> dict:
    """
    Generate a summary of shot data.

    Args:
        df: DataFrame with shot data.

    Returns:
        Dictionary with summary statistics.

    Example:
        >>> df = load_shots_csv('data/sample_shots.csv')
        >>> summary = get_shot_summary(df)
        >>> print(f"FG%: {summary['fg_pct']:.1%}")
    """
    total_shots = len(df)
    made_shots = df['shot_made'].sum()

    # Calculate shooting percentages
    fg_pct = made_shots / total_shots if total_shots > 0 else 0.0

    # 2PT and 3PT breakdowns
    twos = df[df['shot_type'].str.contains('2PT', case=False, na=False)]
    threes = df[df['shot_type'].str.contains('3PT', case=False, na=False)]

    two_made = twos['shot_made'].sum() if len(twos) > 0 else 0
    two_total = len(twos)
    two_pct = two_made / two_total if two_total > 0 else 0.0

    three_made = threes['shot_made'].sum() if len(threes) > 0 else 0
    three_total = len(threes)
    three_pct = three_made / three_total if three_total > 0 else 0.0

    return {
        'total_shots': total_shots,
        'made_shots': int(made_shots),
        'missed_shots': total_shots - int(made_shots),
        'fg_pct': fg_pct,
        'two_pt_made': int(two_made),
        'two_pt_total': two_total,
        'two_pt_pct': two_pct,
        'three_pt_made': int(three_made),
        'three_pt_total': three_total,
        'three_pt_pct': three_pct,
        'unique_players': df['player_name'].nunique(),
        'unique_games': df['game_id'].nunique(),
    }


def filter_shots(
    df: pd.DataFrame,
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    game_id: Optional[str] = None,
    team: Optional[str] = None,
    period: Optional[int] = None,
    shot_type: Optional[str] = None,
    made_only: Optional[bool] = None,
) -> pd.DataFrame:
    """
    Filter shot data by various criteria.

    Args:
        df: DataFrame with shot data.
        player_name: Filter by player name (case-insensitive partial match).
        player_id: Filter by exact player ID.
        game_id: Filter by game ID.
        team: Filter by team abbreviation.
        period: Filter by period number.
        shot_type: Filter by shot type ('2PT' or '3PT').
        made_only: If True, only made shots. If False, only misses. None for all.

    Returns:
        Filtered DataFrame.

    Example:
        >>> df = load_shots_csv('data/sample_shots.csv')
        >>> fox_shots = filter_shots(df, player_name="Fox")
        >>> fox_threes = filter_shots(fox_shots, shot_type="3PT", made_only=True)
    """
    filtered = df.copy()

    if player_name is not None:
        filtered = filtered[
            filtered['player_name'].str.contains(player_name, case=False, na=False)
        ]

    if player_id is not None:
        filtered = filtered[filtered['player_id'] == player_id]

    if game_id is not None:
        filtered = filtered[filtered['game_id'] == str(game_id)]

    if team is not None:
        filtered = filtered[filtered['team'].str.upper() == team.upper()]

    if period is not None:
        filtered = filtered[filtered['period'] == period]

    if shot_type is not None:
        filtered = filtered[
            filtered['shot_type'].str.contains(shot_type, case=False, na=False)
        ]

    if made_only is not None:
        filtered = filtered[filtered['shot_made'] == made_only]

    return filtered
