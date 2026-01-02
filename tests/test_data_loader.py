"""
Unit tests for the data loader module.

Tests verify that:
1. CSV files are loaded correctly
2. Column validation works
3. Data types are converted properly
4. Filtering functions work as expected
5. Edge cases and errors are handled
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.data_loader import (
    load_shots_csv,
    filter_shots,
    get_shot_summary,
    validate_columns,
    convert_dtypes,
    convert_shot_made,
    validate_data_ranges,
    DataValidationError,
    MissingColumnsError,
    InvalidDataTypeError,
    REQUIRED_COLUMNS,
    COLUMN_DTYPES,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_csv_path():
    """Path to the sample shots CSV file."""
    return Path('data/sample_shots.csv')


@pytest.fixture
def sample_df(sample_csv_path):
    """Load the sample shots DataFrame."""
    return load_shots_csv(sample_csv_path)


@pytest.fixture
def valid_shot_data():
    """Create a minimal valid shot DataFrame."""
    return pd.DataFrame({
        'game_id': ['0022300123', '0022300123'],
        'player_id': [203954, 1629029],
        'player_name': ["De'Aaron Fox", "Domantas Sabonis"],
        'team': ['SAC', 'SAC'],
        'period': [1, 2],
        'minutes_remaining': [10, 5],
        'seconds_remaining': [30, 45],
        'shot_made': [True, False],
        'shot_type': ['2PT Field Goal', '3PT Field Goal'],
        'shot_distance': [5.2, 24.3],
        'loc_x': [15.0, -220.0],
        'loc_y': [-8.0, 80.0],
        'shot_zone': ['Paint', 'Left Corner 3'],
        'action_type': ['Driving Layup', 'Jump Shot'],
    })


@pytest.fixture
def temp_csv(tmp_path, valid_shot_data):
    """Create a temporary CSV file with valid shot data."""
    filepath = tmp_path / "test_shots.csv"
    valid_shot_data.to_csv(filepath, index=False)
    return filepath


# =============================================================================
# Test Constants
# =============================================================================

class TestConstants:
    """Test module constants."""

    def test_required_columns_count(self):
        """Should have 14 required columns."""
        assert len(REQUIRED_COLUMNS) == 14

    def test_required_columns_match_dtypes(self):
        """All required columns should have dtype specifications."""
        for col in REQUIRED_COLUMNS:
            assert col in COLUMN_DTYPES, f"Missing dtype for {col}"

    def test_shot_made_is_bool(self):
        """shot_made should be boolean type."""
        assert COLUMN_DTYPES['shot_made'] == bool

    def test_coordinates_are_float(self):
        """Coordinate columns should be float type."""
        assert COLUMN_DTYPES['loc_x'] == float
        assert COLUMN_DTYPES['loc_y'] == float
        assert COLUMN_DTYPES['shot_distance'] == float


# =============================================================================
# Test convert_shot_made Function
# =============================================================================

class TestConvertShotMade:
    """Test the shot_made boolean conversion."""

    def test_boolean_true(self):
        """Boolean True stays True."""
        assert convert_shot_made(True) is True

    def test_boolean_false(self):
        """Boolean False stays False."""
        assert convert_shot_made(False) is False

    def test_string_true_variants(self):
        """Various string representations of True."""
        for val in ['True', 'true', 'TRUE', '1', 'yes', 'YES', 'made', 'MADE', 'y']:
            assert convert_shot_made(val) is True, f"Failed for: {val}"

    def test_string_false_variants(self):
        """Various string representations of False."""
        for val in ['False', 'false', 'FALSE', '0', 'no', 'NO', 'missed', 'MISSED', 'n']:
            assert convert_shot_made(val) is False, f"Failed for: {val}"

    def test_numeric_one(self):
        """Numeric 1 converts to True."""
        assert convert_shot_made(1) is True
        assert convert_shot_made(1.0) is True

    def test_numeric_zero(self):
        """Numeric 0 converts to False."""
        assert convert_shot_made(0) is False
        assert convert_shot_made(0.0) is False

    def test_nan_returns_none(self):
        """NaN values return None."""
        assert convert_shot_made(np.nan) is None
        assert convert_shot_made(pd.NA) is None

    def test_invalid_string_raises(self):
        """Invalid strings raise ValueError."""
        with pytest.raises(ValueError):
            convert_shot_made("maybe")


# =============================================================================
# Test validate_columns Function
# =============================================================================

class TestValidateColumns:
    """Test column validation."""

    def test_valid_columns_pass(self, valid_shot_data):
        """Valid DataFrame passes validation."""
        # Should not raise
        validate_columns(valid_shot_data)

    def test_missing_single_column(self, valid_shot_data):
        """Missing single column raises MissingColumnsError."""
        df = valid_shot_data.drop(columns=['game_id'])
        with pytest.raises(MissingColumnsError) as exc_info:
            validate_columns(df)
        assert 'game_id' in exc_info.value.missing_columns

    def test_missing_multiple_columns(self, valid_shot_data):
        """Missing multiple columns are all reported."""
        df = valid_shot_data.drop(columns=['game_id', 'player_id', 'team'])
        with pytest.raises(MissingColumnsError) as exc_info:
            validate_columns(df)
        assert len(exc_info.value.missing_columns) == 3

    def test_extra_columns_ok(self, valid_shot_data):
        """Extra columns don't cause errors."""
        valid_shot_data['extra_col'] = 'extra'
        # Should not raise
        validate_columns(valid_shot_data)


# =============================================================================
# Test convert_dtypes Function
# =============================================================================

class TestConvertDtypes:
    """Test data type conversion."""

    def test_game_id_to_string(self, valid_shot_data):
        """game_id is converted to string."""
        df = convert_dtypes(valid_shot_data)
        assert df['game_id'].dtype == object  # pandas string type

    def test_player_id_to_int(self, valid_shot_data):
        """player_id is converted to nullable integer."""
        df = convert_dtypes(valid_shot_data)
        assert df['player_id'].dtype == 'Int64'

    def test_shot_made_to_bool(self, valid_shot_data):
        """shot_made is converted to boolean."""
        # Use string values to test conversion
        valid_shot_data['shot_made'] = ['True', 'False']
        df = convert_dtypes(valid_shot_data)
        assert df['shot_made'].iloc[0] == True
        assert df['shot_made'].iloc[1] == False

    def test_coordinates_to_float(self, valid_shot_data):
        """Coordinate columns are converted to float."""
        df = convert_dtypes(valid_shot_data)
        assert df['loc_x'].dtype == float
        assert df['loc_y'].dtype == float
        assert df['shot_distance'].dtype == float

    def test_period_to_int(self, valid_shot_data):
        """Period columns are converted to integer."""
        df = convert_dtypes(valid_shot_data)
        assert df['period'].dtype == 'Int64'
        assert df['minutes_remaining'].dtype == 'Int64'
        assert df['seconds_remaining'].dtype == 'Int64'


# =============================================================================
# Test validate_data_ranges Function
# =============================================================================

class TestValidateDataRanges:
    """Test data range validation."""

    def test_valid_data_no_warnings(self, valid_shot_data):
        """Valid data produces no warnings."""
        df = convert_dtypes(valid_shot_data)
        warnings = validate_data_ranges(df)
        assert len(warnings) == 0

    def test_invalid_period_warning(self, valid_shot_data):
        """Invalid period values produce warning."""
        valid_shot_data['period'] = [0, 15]  # Invalid periods
        df = convert_dtypes(valid_shot_data)
        warnings = validate_data_ranges(df)
        assert any('period' in w for w in warnings)

    def test_invalid_minutes_warning(self, valid_shot_data):
        """Invalid minutes produce warning."""
        valid_shot_data['minutes_remaining'] = [15, -1]  # Invalid
        df = convert_dtypes(valid_shot_data)
        warnings = validate_data_ranges(df)
        assert any('minutes' in w for w in warnings)

    def test_strict_mode_raises(self, valid_shot_data):
        """Strict mode raises on warnings."""
        valid_shot_data['period'] = [0, 0]  # Invalid
        df = convert_dtypes(valid_shot_data)
        with pytest.raises(DataValidationError):
            validate_data_ranges(df, strict=True)


# =============================================================================
# Test load_shots_csv Function
# =============================================================================

class TestLoadShotsCsv:
    """Test the main CSV loading function."""

    def test_load_sample_csv(self, sample_csv_path):
        """Can load the sample CSV file."""
        df = load_shots_csv(sample_csv_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_load_temp_csv(self, temp_csv):
        """Can load a temporary CSV file."""
        df = load_shots_csv(temp_csv)
        assert len(df) == 2

    def test_file_not_found(self):
        """Missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_shots_csv('nonexistent_file.csv')

    def test_wrong_extension(self, tmp_path):
        """Non-CSV extension raises ValueError."""
        filepath = tmp_path / "data.txt"
        filepath.write_text("some data")
        with pytest.raises(ValueError) as exc_info:
            load_shots_csv(filepath)
        assert 'CSV' in str(exc_info.value)

    def test_empty_csv(self, tmp_path):
        """Empty CSV raises DataValidationError."""
        filepath = tmp_path / "empty.csv"
        filepath.write_text("col1,col2,col3\n")  # Headers only
        with pytest.raises(DataValidationError) as exc_info:
            load_shots_csv(filepath)
        assert 'empty' in str(exc_info.value).lower()

    def test_missing_columns_csv(self, tmp_path):
        """CSV with missing columns raises MissingColumnsError."""
        filepath = tmp_path / "incomplete.csv"
        filepath.write_text("game_id,player_name\n123,Fox\n")
        with pytest.raises(MissingColumnsError):
            load_shots_csv(filepath)

    def test_skip_validation(self, tmp_path):
        """Can skip validation with validate=False."""
        filepath = tmp_path / "minimal.csv"
        filepath.write_text("game_id,player_name\n123,Fox\n")
        # Should not raise with validate=False
        df = load_shots_csv(filepath, validate=False)
        assert len(df) == 1

    def test_correct_dtypes_after_load(self, sample_csv_path):
        """Loaded data has correct dtypes."""
        df = load_shots_csv(sample_csv_path)
        assert df['game_id'].dtype == object
        assert df['player_id'].dtype == 'Int64'
        assert df['loc_x'].dtype == float


# =============================================================================
# Test get_shot_summary Function
# =============================================================================

class TestGetShotSummary:
    """Test shot summary statistics."""

    def test_summary_keys(self, sample_df):
        """Summary contains all expected keys."""
        summary = get_shot_summary(sample_df)
        expected_keys = [
            'total_shots', 'made_shots', 'missed_shots', 'fg_pct',
            'two_pt_made', 'two_pt_total', 'two_pt_pct',
            'three_pt_made', 'three_pt_total', 'three_pt_pct',
            'unique_players', 'unique_games',
        ]
        for key in expected_keys:
            assert key in summary, f"Missing key: {key}"

    def test_total_shots_count(self, sample_df):
        """Total shots matches DataFrame length."""
        summary = get_shot_summary(sample_df)
        assert summary['total_shots'] == len(sample_df)

    def test_made_plus_missed_equals_total(self, sample_df):
        """Made + missed = total."""
        summary = get_shot_summary(sample_df)
        assert summary['made_shots'] + summary['missed_shots'] == summary['total_shots']

    def test_fg_percentage_calculation(self, valid_shot_data):
        """FG% is calculated correctly."""
        # 1 made, 1 missed = 50%
        df = convert_dtypes(valid_shot_data)
        summary = get_shot_summary(df)
        assert summary['fg_pct'] == 0.5

    def test_two_and_three_point_totals(self, sample_df):
        """2PT + 3PT totals match overall total."""
        summary = get_shot_summary(sample_df)
        assert summary['two_pt_total'] + summary['three_pt_total'] == summary['total_shots']


# =============================================================================
# Test filter_shots Function
# =============================================================================

class TestFilterShots:
    """Test shot filtering functionality."""

    def test_filter_by_player_name(self, sample_df):
        """Can filter by player name (partial match)."""
        filtered = filter_shots(sample_df, player_name="Fox")
        assert len(filtered) > 0
        assert all(filtered['player_name'].str.contains('Fox'))

    def test_filter_by_player_name_case_insensitive(self, sample_df):
        """Player name filter is case-insensitive."""
        filtered1 = filter_shots(sample_df, player_name="fox")
        filtered2 = filter_shots(sample_df, player_name="FOX")
        assert len(filtered1) == len(filtered2)

    def test_filter_by_player_id(self, sample_df):
        """Can filter by exact player ID."""
        # De'Aaron Fox's ID
        filtered = filter_shots(sample_df, player_id=203954)
        assert len(filtered) > 0
        assert all(filtered['player_id'] == 203954)

    def test_filter_by_team(self, sample_df):
        """Can filter by team abbreviation."""
        filtered = filter_shots(sample_df, team="SAC")
        assert len(filtered) == len(sample_df)  # All SAC in sample

    def test_filter_by_period(self, sample_df):
        """Can filter by period."""
        filtered = filter_shots(sample_df, period=1)
        assert len(filtered) > 0
        assert all(filtered['period'] == 1)

    def test_filter_by_shot_type_2pt(self, sample_df):
        """Can filter for 2PT shots."""
        filtered = filter_shots(sample_df, shot_type="2PT")
        assert len(filtered) > 0
        assert all(filtered['shot_type'].str.contains('2PT'))

    def test_filter_by_shot_type_3pt(self, sample_df):
        """Can filter for 3PT shots."""
        filtered = filter_shots(sample_df, shot_type="3PT")
        assert len(filtered) > 0
        assert all(filtered['shot_type'].str.contains('3PT'))

    def test_filter_made_only(self, sample_df):
        """Can filter for made shots only."""
        filtered = filter_shots(sample_df, made_only=True)
        assert len(filtered) > 0
        assert all(filtered['shot_made'] == True)

    def test_filter_missed_only(self, sample_df):
        """Can filter for missed shots only."""
        filtered = filter_shots(sample_df, made_only=False)
        assert len(filtered) > 0
        assert all(filtered['shot_made'] == False)

    def test_multiple_filters(self, sample_df):
        """Can apply multiple filters at once."""
        filtered = filter_shots(
            sample_df,
            player_name="Fox",
            shot_type="3PT",
            made_only=False,
        )
        # Should be Fox's missed 3-pointers
        if len(filtered) > 0:
            assert all(filtered['player_name'].str.contains('Fox'))
            assert all(filtered['shot_type'].str.contains('3PT'))
            assert all(filtered['shot_made'] == False)

    def test_filter_no_match_returns_empty(self, sample_df):
        """Filter with no matches returns empty DataFrame."""
        filtered = filter_shots(sample_df, player_name="NonexistentPlayer")
        assert len(filtered) == 0
        assert isinstance(filtered, pd.DataFrame)

    def test_filter_preserves_columns(self, sample_df):
        """Filtering preserves all columns."""
        filtered = filter_shots(sample_df, player_name="Fox")
        assert list(filtered.columns) == list(sample_df.columns)


# =============================================================================
# Test Error Classes
# =============================================================================

class TestErrorClasses:
    """Test custom exception classes."""

    def test_missing_columns_error_message(self):
        """MissingColumnsError has descriptive message."""
        err = MissingColumnsError(['col1', 'col2'])
        assert 'col1' in str(err)
        assert 'col2' in str(err)
        assert err.missing_columns == ['col1', 'col2']

    def test_invalid_data_type_error_message(self):
        """InvalidDataTypeError has descriptive message."""
        err = InvalidDataTypeError('test_col', 'integer', 'parse error')
        assert 'test_col' in str(err)
        assert 'integer' in str(err)
        assert err.column == 'test_col'
        assert err.expected_type == 'integer'

    def test_data_validation_error_inheritance(self):
        """All errors inherit from DataValidationError."""
        assert issubclass(MissingColumnsError, DataValidationError)
        assert issubclass(InvalidDataTypeError, DataValidationError)


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests with real sample data."""

    def test_full_workflow(self, sample_csv_path):
        """Test complete load -> filter -> summarize workflow."""
        # Load data
        df = load_shots_csv(sample_csv_path)
        assert len(df) > 0

        # Filter to one player
        fox_shots = filter_shots(df, player_name="Fox")
        assert len(fox_shots) > 0

        # Get summary
        summary = get_shot_summary(fox_shots)
        assert summary['total_shots'] == len(fox_shots)
        assert summary['unique_players'] == 1

    def test_sample_data_has_expected_content(self, sample_df):
        """Sample data contains expected players and teams."""
        players = sample_df['player_name'].unique()
        assert "De'Aaron Fox" in players

        teams = sample_df['team'].unique()
        assert 'SAC' in teams

    def test_sample_data_coordinates_valid(self, sample_df):
        """Sample data has valid coordinate ranges."""
        # loc_x should be within court bounds
        assert sample_df['loc_x'].min() >= -250
        assert sample_df['loc_x'].max() <= 250

        # loc_y can be negative (behind baseline) in NBA API coords
        # Valid range is roughly -200 to 450
        assert sample_df['loc_y'].min() >= -200
        assert sample_df['loc_y'].max() <= 450
