"""
Unit tests for the NBA API client module.

Tests use mock data to avoid hitting the real API.
Tests verify:
1. Data transformation from API format to our schema
2. Player and team ID lookup
3. Caching functionality
4. Error handling
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.data.nba_api_client import (
    NBAApiClient,
    NBAApiError,
    PlayerNotFoundError,
    GameNotFoundError,
    RateLimitError,
)


# =============================================================================
# Mock Data
# =============================================================================

MOCK_SHOT_DATA = {
    'GAME_ID': ['0022400001', '0022400001', '0022400001'],
    'PLAYER_ID': [1628368, 1628368, 1629029],
    'PLAYER_NAME': ["De'Aaron Fox", "De'Aaron Fox", "Domantas Sabonis"],
    'TEAM_ABBREVIATION': ['SAC', 'SAC', 'SAC'],
    'TEAM_NAME': ['Sacramento Kings', 'Sacramento Kings', 'Sacramento Kings'],
    'PERIOD': [1, 1, 2],
    'MINUTES_REMAINING': [10, 8, 6],
    'SECONDS_REMAINING': [30, 45, 15],
    'SHOT_MADE_FLAG': [1, 0, 1],
    'SHOT_TYPE': ['2PT Field Goal', '3PT Field Goal', '2PT Field Goal'],
    'SHOT_DISTANCE': [5, 24, 3],
    'LOC_X': [15, -180, 10],
    'LOC_Y': [25, 90, 20],
    'SHOT_ZONE_BASIC': ['Restricted Area', 'Left Side(L)', 'Restricted Area'],
    'ACTION_TYPE': ['Driving Layup Shot', 'Jump Shot', 'Dunk Shot'],
}

MOCK_SCHEDULE_DATA = {
    'GAME_ID': ['0022400003', '0022400002', '0022400001'],
    'GAME_DATE': ['2024-01-03', '2024-01-01', '2023-12-30'],
    'MATCHUP': ['SAC vs. LAL', 'SAC @ GSW', 'SAC vs. PHX'],
    'WL': ['W', 'L', 'W'],
    'PTS': [120, 108, 115],
    'PLUS_MINUS': [10, -5, 8],
}

MOCK_PLAYERS = [
    {'id': 1628368, 'full_name': "De'Aaron Fox", 'first_name': "De'Aaron", 'last_name': 'Fox'},
    {'id': 1629029, 'full_name': 'Domantas Sabonis', 'first_name': 'Domantas', 'last_name': 'Sabonis'},
    {'id': 1628398, 'full_name': 'Keegan Murray', 'first_name': 'Keegan', 'last_name': 'Murray'},
]

MOCK_TEAMS = [
    {'id': 1610612758, 'abbreviation': 'SAC', 'full_name': 'Sacramento Kings'},
    {'id': 1610612747, 'abbreviation': 'LAL', 'full_name': 'Los Angeles Lakers'},
    {'id': 1610612744, 'abbreviation': 'GSW', 'full_name': 'Golden State Warriors'},
]


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_shot_df():
    """Create mock shot DataFrame from API."""
    return pd.DataFrame(MOCK_SHOT_DATA)


@pytest.fixture
def mock_schedule_df():
    """Create mock schedule DataFrame."""
    return pd.DataFrame(MOCK_SCHEDULE_DATA)


@pytest.fixture
def client(tmp_path):
    """Create client with temp cache directory."""
    return NBAApiClient(cache_dir=tmp_path, use_cache=True, request_delay=0)


@pytest.fixture
def client_no_cache(tmp_path):
    """Create client with caching disabled."""
    return NBAApiClient(cache_dir=tmp_path, use_cache=False, request_delay=0)


# =============================================================================
# Test Initialization
# =============================================================================

class TestNBAApiClientInit:
    """Test client initialization."""

    def test_init_default_cache_dir(self):
        """Default cache dir is data/cache."""
        client = NBAApiClient()
        assert 'cache' in str(client.cache_dir)

    def test_init_custom_cache_dir(self, tmp_path):
        """Can set custom cache directory."""
        client = NBAApiClient(cache_dir=tmp_path)
        assert client.cache_dir == tmp_path

    def test_init_creates_cache_dir(self, tmp_path):
        """Cache directory is created if it doesn't exist."""
        cache_path = tmp_path / "new_cache"
        client = NBAApiClient(cache_dir=cache_path)
        assert cache_path.exists()

    def test_init_use_cache_default(self, tmp_path):
        """Caching is enabled by default."""
        client = NBAApiClient(cache_dir=tmp_path)
        assert client.use_cache is True

    def test_init_disable_cache(self, tmp_path):
        """Can disable caching."""
        client = NBAApiClient(cache_dir=tmp_path, use_cache=False)
        assert client.use_cache is False

    def test_init_request_delay(self, tmp_path):
        """Can set request delay."""
        client = NBAApiClient(cache_dir=tmp_path, request_delay=1.0)
        assert client.request_delay == 1.0


# =============================================================================
# Test Data Transformation
# =============================================================================

class TestDataTransformation:
    """Test transformation from API format to our schema."""

    def test_transform_renames_columns(self, client, mock_shot_df):
        """Columns are renamed to our schema."""
        result = client._transform_shot_data(mock_shot_df)

        assert 'game_id' in result.columns
        assert 'player_id' in result.columns
        assert 'player_name' in result.columns
        assert 'team' in result.columns
        assert 'shot_made' in result.columns
        assert 'loc_x' in result.columns
        assert 'loc_y' in result.columns

    def test_transform_shot_made_to_bool(self, client, mock_shot_df):
        """shot_made is converted to boolean."""
        result = client._transform_shot_data(mock_shot_df)

        assert result['shot_made'].dtype == bool
        assert result['shot_made'].iloc[0] == True
        assert result['shot_made'].iloc[1] == False

    def test_transform_player_id_type(self, client, mock_shot_df):
        """player_id is nullable integer."""
        result = client._transform_shot_data(mock_shot_df)
        assert result['player_id'].dtype == 'Int64'

    def test_transform_coordinates_numeric(self, client, mock_shot_df):
        """Coordinates are numeric."""
        result = client._transform_shot_data(mock_shot_df)

        assert pd.api.types.is_numeric_dtype(result['loc_x'])
        assert pd.api.types.is_numeric_dtype(result['loc_y'])
        assert pd.api.types.is_numeric_dtype(result['shot_distance'])

    def test_transform_empty_dataframe(self, client):
        """Empty DataFrame returns empty result."""
        result = client._transform_shot_data(pd.DataFrame())
        assert result.empty

    def test_transform_preserves_values(self, client, mock_shot_df):
        """Data values are preserved correctly."""
        result = client._transform_shot_data(mock_shot_df)

        assert result.iloc[0]['game_id'] == '0022400001'
        assert result.iloc[0]['player_name'] == "De'Aaron Fox"
        assert result.iloc[0]['loc_x'] == 15
        assert result.iloc[0]['loc_y'] == 25


# =============================================================================
# Test Player ID Lookup
# =============================================================================

class TestFindPlayerId:
    """Test player ID lookup functionality."""

    @patch('src.data.nba_api_client.players.get_players')
    def test_find_player_exact_match(self, mock_get_players, client):
        """Finds player with exact name match."""
        mock_get_players.return_value = MOCK_PLAYERS

        player_id = client.find_player_id("De'Aaron Fox")
        assert player_id == 1628368

    @patch('src.data.nba_api_client.players.get_players')
    def test_find_player_partial_match(self, mock_get_players, client):
        """Finds player with partial name match."""
        mock_get_players.return_value = MOCK_PLAYERS

        player_id = client.find_player_id("Fox")
        assert player_id == 1628368

    @patch('src.data.nba_api_client.players.get_players')
    def test_find_player_case_insensitive(self, mock_get_players, client):
        """Search is case insensitive."""
        mock_get_players.return_value = MOCK_PLAYERS

        player_id = client.find_player_id("de'aaron fox")
        assert player_id == 1628368

    @patch('src.data.nba_api_client.players.get_players')
    def test_find_player_not_found(self, mock_get_players, client):
        """Raises error when player not found."""
        mock_get_players.return_value = MOCK_PLAYERS

        with pytest.raises(PlayerNotFoundError):
            client.find_player_id("NonexistentPlayer")


# =============================================================================
# Test Team ID Lookup
# =============================================================================

class TestFindTeamId:
    """Test team ID lookup functionality."""

    @patch('src.data.nba_api_client.teams.get_teams')
    def test_find_team_by_abbrev(self, mock_get_teams, client):
        """Finds team by abbreviation."""
        mock_get_teams.return_value = MOCK_TEAMS

        team_id = client.find_team_id("SAC")
        assert team_id == 1610612758

    @patch('src.data.nba_api_client.teams.get_teams')
    def test_find_team_case_insensitive(self, mock_get_teams, client):
        """Team search is case insensitive."""
        mock_get_teams.return_value = MOCK_TEAMS

        team_id = client.find_team_id("sac")
        assert team_id == 1610612758

    @patch('src.data.nba_api_client.teams.get_teams')
    def test_find_team_not_found(self, mock_get_teams, client):
        """Raises error when team not found."""
        mock_get_teams.return_value = MOCK_TEAMS

        with pytest.raises(NBAApiError):
            client.find_team_id("XXX")


# =============================================================================
# Test Caching
# =============================================================================

class TestCaching:
    """Test caching functionality."""

    def test_save_and_load_cache(self, client, mock_shot_df):
        """Data can be saved and loaded from cache."""
        transformed = client._transform_shot_data(mock_shot_df)

        # Save to cache
        client._save_to_cache("test_key", transformed)

        # Load from cache
        loaded = client._load_from_cache("test_key")

        assert loaded is not None
        assert len(loaded) == len(transformed)
        assert list(loaded.columns) == list(transformed.columns)

    def test_cache_miss_returns_none(self, client):
        """Cache miss returns None."""
        result = client._load_from_cache("nonexistent_key")
        assert result is None

    def test_cache_disabled(self, client_no_cache, mock_shot_df):
        """Cache operations are no-op when disabled."""
        transformed = client_no_cache._transform_shot_data(mock_shot_df)

        # Save should do nothing
        client_no_cache._save_to_cache("test_key", transformed)

        # Load should return None
        loaded = client_no_cache._load_from_cache("test_key")
        assert loaded is None

    def test_clear_cache(self, client, mock_shot_df):
        """Can clear all cached data."""
        transformed = client._transform_shot_data(mock_shot_df)

        # Save multiple items
        client._save_to_cache("key1", transformed)
        client._save_to_cache("key2", transformed)

        # Clear cache
        count = client.clear_cache()
        assert count == 2

        # Verify cleared
        assert client._load_from_cache("key1") is None
        assert client._load_from_cache("key2") is None


# =============================================================================
# Test API Methods with Mocks
# =============================================================================

class TestGetGameShots:
    """Test get_game_shots method."""

    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_game_shots_success(self, mock_request, client, mock_shot_df):
        """Successfully fetches game shots."""
        mock_request.return_value = mock_shot_df

        result = client.get_game_shots("0022400001")

        assert len(result) == 3
        assert 'game_id' in result.columns
        assert 'shot_made' in result.columns

    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_game_shots_empty(self, mock_request, client):
        """Raises error when no shots found."""
        mock_request.return_value = pd.DataFrame()

        with pytest.raises(GameNotFoundError):
            client.get_game_shots("0022400999")

    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_game_shots_uses_cache(self, mock_request, client, mock_shot_df):
        """Uses cached data on second call."""
        mock_request.return_value = mock_shot_df

        # First call hits API
        result1 = client.get_game_shots("0022400001")
        assert mock_request.call_count == 1

        # Second call should use cache
        result2 = client.get_game_shots("0022400001")
        assert mock_request.call_count == 1  # No additional call

        assert len(result1) == len(result2)


class TestGetPlayerShots:
    """Test get_player_shots method."""

    @patch('src.data.nba_api_client.players.get_players')
    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_player_shots_success(self, mock_request, mock_get_players, client, mock_shot_df):
        """Successfully fetches player shots."""
        mock_get_players.return_value = MOCK_PLAYERS
        mock_request.return_value = mock_shot_df

        result = client.get_player_shots("De'Aaron Fox", "2023-24")

        assert len(result) == 3
        assert mock_request.called

    @patch('src.data.nba_api_client.players.get_players')
    def test_get_player_shots_player_not_found(self, mock_get_players, client):
        """Raises error when player not found."""
        mock_get_players.return_value = MOCK_PLAYERS

        with pytest.raises(PlayerNotFoundError):
            client.get_player_shots("Unknown Player", "2023-24")


class TestGetTeamSchedule:
    """Test get_team_schedule method."""

    @patch('src.data.nba_api_client.teams.get_teams')
    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_team_schedule_success(self, mock_request, mock_get_teams, client, mock_schedule_df):
        """Successfully fetches team schedule."""
        mock_get_teams.return_value = MOCK_TEAMS
        mock_request.return_value = mock_schedule_df

        result = client.get_team_schedule("SAC", "2023-24")

        assert len(result) == 3
        assert 'game_id' in result.columns
        assert 'matchup' in result.columns

    @patch('src.data.nba_api_client.teams.get_teams')
    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_team_schedule_sorted_by_date(self, mock_request, mock_get_teams, client, mock_schedule_df):
        """Schedule is sorted by date descending."""
        mock_get_teams.return_value = MOCK_TEAMS
        mock_request.return_value = mock_schedule_df

        result = client.get_team_schedule("SAC", "2023-24")

        # Most recent game should be first
        assert result.iloc[0]['game_id'] == '0022400003'


class TestGetRecentKingsGame:
    """Test get_recent_kings_game method."""

    @patch('src.data.nba_api_client.teams.get_teams')
    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_recent_game(self, mock_request, mock_get_teams, client, mock_schedule_df):
        """Gets most recent Kings game."""
        mock_get_teams.return_value = MOCK_TEAMS
        mock_request.return_value = mock_schedule_df

        result = client.get_recent_kings_game("2023-24")

        assert result['game_id'] == '0022400003'
        assert result['matchup'] == 'SAC vs. LAL'
        assert result['result'] == 'W'

    @patch('src.data.nba_api_client.teams.get_teams')
    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_get_recent_game_no_games(self, mock_request, mock_get_teams, client):
        """Raises error when no games found."""
        mock_get_teams.return_value = MOCK_TEAMS
        mock_request.return_value = pd.DataFrame()

        with pytest.raises(GameNotFoundError):
            client.get_recent_kings_game("2023-24")


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Test error handling."""

    def test_nba_api_error_is_exception(self):
        """NBAApiError inherits from Exception."""
        assert issubclass(NBAApiError, Exception)

    def test_player_not_found_error(self):
        """PlayerNotFoundError has correct inheritance."""
        assert issubclass(PlayerNotFoundError, NBAApiError)

    def test_game_not_found_error(self):
        """GameNotFoundError has correct inheritance."""
        assert issubclass(GameNotFoundError, NBAApiError)

    def test_rate_limit_error(self):
        """RateLimitError has correct inheritance."""
        assert issubclass(RateLimitError, NBAApiError)

    @patch.object(NBAApiClient, '_api_request_with_retry')
    def test_api_error_propagates(self, mock_request, client):
        """API errors are properly propagated."""
        mock_request.side_effect = NBAApiError("Test error")

        with pytest.raises(NBAApiError):
            client.get_game_shots("0022400001")


# =============================================================================
# Test Rate Limiting
# =============================================================================

class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_delays_requests(self, tmp_path):
        """Rate limiting adds delay between requests."""
        import time

        client = NBAApiClient(cache_dir=tmp_path, request_delay=0.1)

        start = time.time()
        client._rate_limit()
        client._rate_limit()
        elapsed = time.time() - start

        # Should have waited at least 0.1 seconds
        assert elapsed >= 0.1
