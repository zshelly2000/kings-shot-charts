"""
NBA API Client for Kings Shot Chart Generator.

This module provides the NBAApiClient class for fetching shot data
from the official NBA Stats API using the nba_api package.

Example:
    >>> from src.data.nba_api_client import NBAApiClient
    >>> client = NBAApiClient()
    >>> shots = client.get_game_shots("0022400001")
    >>> print(f"Fetched {len(shots)} shots")
"""

import json
import time
from pathlib import Path
from typing import Optional, Union, List
from datetime import datetime

import pandas as pd

from nba_api.stats.endpoints import (
    shotchartdetail,
    commonplayerinfo,
    leaguegamefinder,
    playergamelog,
)
from nba_api.stats.static import players, teams

from src.utils.config import (
    KINGS_TEAM_ID,
    KINGS_ABBREVIATION,
    DEFAULT_SEASON,
    API_TIMEOUT,
    API_RETRY_COUNT,
    API_RETRY_DELAY,
)


class NBAApiError(Exception):
    """Base exception for NBA API errors."""
    pass


class PlayerNotFoundError(NBAApiError):
    """Raised when a player cannot be found."""
    pass


class GameNotFoundError(NBAApiError):
    """Raised when a game cannot be found."""
    pass


class RateLimitError(NBAApiError):
    """Raised when API rate limit is hit."""
    pass


class NBAApiClient:
    """
    Client for fetching shot data from the NBA Stats API.

    Provides methods to fetch shot chart data for games, players,
    and teams. Includes caching to reduce API calls and respect
    rate limits.

    Attributes:
        cache_dir: Directory for caching API responses.
        use_cache: Whether to use cached data when available.
        request_delay: Seconds to wait between API requests.

    Example:
        >>> client = NBAApiClient()
        >>> fox_shots = client.get_player_shots("De'Aaron Fox", "2023-24")
        >>> print(f"Fox took {len(fox_shots)} shots")
    """

    # Column mapping from NBA API to our schema
    COLUMN_MAPPING = {
        'GAME_ID': 'game_id',
        'PLAYER_ID': 'player_id',
        'PLAYER_NAME': 'player_name',
        'TEAM_NAME': 'team_name',
        'TEAM_ABBREVIATION': 'team',
        'PERIOD': 'period',
        'MINUTES_REMAINING': 'minutes_remaining',
        'SECONDS_REMAINING': 'seconds_remaining',
        'SHOT_MADE_FLAG': 'shot_made',
        'SHOT_TYPE': 'shot_type',
        'SHOT_DISTANCE': 'shot_distance',
        'LOC_X': 'loc_x',
        'LOC_Y': 'loc_y',
        'SHOT_ZONE_BASIC': 'shot_zone',
        'ACTION_TYPE': 'action_type',
        'EVENT_TYPE': 'event_type',
        'SHOT_ZONE_AREA': 'shot_zone_area',
        'SHOT_ZONE_RANGE': 'shot_zone_range',
        'GAME_DATE': 'game_date',
        'HTM': 'home_team',
        'VTM': 'away_team',
    }

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        use_cache: bool = True,
        request_delay: float = 0.6,
    ) -> None:
        """
        Initialize the NBA API client.

        Args:
            cache_dir: Directory for caching responses. Defaults to data/cache/.
            use_cache: Whether to use cached data. Default True.
            request_delay: Seconds between API requests. Default 0.6.
        """
        if cache_dir is None:
            # Default to project's data/cache directory
            self.cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
        else:
            self.cache_dir = Path(cache_dir)

        self.use_cache = use_cache
        self.request_delay = request_delay
        self._last_request_time = 0.0

        # Create cache directory if needed
        if self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _rate_limit(self) -> None:
        """
        Enforce rate limiting between API requests.

        Waits if necessary to ensure minimum delay between requests.
        """
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        safe_key = cache_key.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"

    def _load_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """
        Load data from cache if available.

        Args:
            cache_key: Unique identifier for the cached data.

        Returns:
            DataFrame if cache hit, None if miss.
        """
        if not self.use_cache:
            return None

        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                return pd.DataFrame(data)
            except (json.JSONDecodeError, KeyError):
                # Invalid cache, ignore
                return None
        return None

    def _save_to_cache(self, cache_key: str, df: pd.DataFrame) -> None:
        """
        Save data to cache.

        Args:
            cache_key: Unique identifier for the cached data.
            df: DataFrame to cache.
        """
        if not self.use_cache:
            return

        cache_path = self._get_cache_path(cache_key)
        try:
            # Convert to records for JSON serialization
            data = df.to_dict(orient='records')
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception:
            # Cache write failures are not critical
            pass

    def _api_request_with_retry(self, endpoint_func, **kwargs) -> pd.DataFrame:
        """
        Make an API request with retry logic.

        Args:
            endpoint_func: The nba_api endpoint function to call.
            **kwargs: Arguments to pass to the endpoint.

        Returns:
            DataFrame from the API response.

        Raises:
            NBAApiError: If all retries fail.
        """
        last_error = None

        for attempt in range(API_RETRY_COUNT):
            try:
                self._rate_limit()
                endpoint = endpoint_func(**kwargs, timeout=API_TIMEOUT)
                dfs = endpoint.get_data_frames()
                return dfs[0] if len(dfs) > 0 else pd.DataFrame()
            except Exception as e:
                last_error = e
                if "rate" in str(e).lower() or "429" in str(e):
                    raise RateLimitError(f"API rate limit hit: {e}")
                if attempt < API_RETRY_COUNT - 1:
                    time.sleep(API_RETRY_DELAY * (attempt + 1))

        raise NBAApiError(f"API request failed after {API_RETRY_COUNT} attempts: {last_error}")

    def _transform_shot_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform NBA API shot data to our schema.

        Args:
            df: Raw DataFrame from NBA API.

        Returns:
            DataFrame matching our Shot data schema.
        """
        if df.empty:
            return pd.DataFrame()

        # Make a copy to avoid modifying original
        df = df.copy()

        # Derive team abbreviation from TEAM_NAME if not present
        if 'TEAM_ABBREVIATION' not in df.columns and 'TEAM_NAME' in df.columns:
            # Map team names to abbreviations
            team_abbrev_map = {team['full_name']: team['abbreviation']
                              for team in teams.get_teams()}
            df['TEAM_ABBREVIATION'] = df['TEAM_NAME'].map(team_abbrev_map)

        # Rename columns to our schema
        df = df.rename(columns=self.COLUMN_MAPPING)

        # Select only the columns we need
        our_columns = [
            'game_id', 'player_id', 'player_name', 'team', 'period',
            'minutes_remaining', 'seconds_remaining', 'shot_made',
            'shot_type', 'shot_distance', 'loc_x', 'loc_y',
            'shot_zone', 'action_type'
        ]

        # Keep only columns that exist
        available_columns = [c for c in our_columns if c in df.columns]
        df = df[available_columns].copy()

        # Convert shot_made to boolean
        if 'shot_made' in df.columns:
            df['shot_made'] = df['shot_made'].astype(bool)

        # Convert types
        if 'player_id' in df.columns:
            df['player_id'] = df['player_id'].astype('Int64')
        if 'period' in df.columns:
            df['period'] = df['period'].astype('Int64')
        if 'minutes_remaining' in df.columns:
            df['minutes_remaining'] = df['minutes_remaining'].astype('Int64')
        if 'seconds_remaining' in df.columns:
            df['seconds_remaining'] = df['seconds_remaining'].astype('Int64')

        # Ensure numeric types for coordinates
        for col in ['shot_distance', 'loc_x', 'loc_y']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def find_player_id(self, player_name: str) -> int:
        """
        Find NBA player ID by name.

        Searches for players matching the given name. Supports partial
        matching (e.g., "Fox" will find "De'Aaron Fox").

        Args:
            player_name: Player name to search for.

        Returns:
            NBA player ID.

        Raises:
            PlayerNotFoundError: If no matching player found.

        Example:
            >>> client = NBAApiClient()
            >>> fox_id = client.find_player_id("De'Aaron Fox")
            >>> print(fox_id)  # 1628368
        """
        # Search in static player list
        all_players = players.get_players()

        # Try exact match first
        for player in all_players:
            if player['full_name'].lower() == player_name.lower():
                return player['id']

        # Try partial match
        matches = []
        search_lower = player_name.lower()
        for player in all_players:
            if search_lower in player['full_name'].lower():
                matches.append(player)

        if len(matches) == 1:
            return matches[0]['id']
        elif len(matches) > 1:
            # Return most recent active player or first match
            # For now, just return first match
            return matches[0]['id']
        else:
            raise PlayerNotFoundError(f"No player found matching: {player_name}")

    def find_team_id(self, team_abbrev: str) -> int:
        """
        Find NBA team ID by abbreviation.

        Args:
            team_abbrev: Team abbreviation (e.g., "SAC", "LAL").

        Returns:
            NBA team ID.

        Raises:
            NBAApiError: If team not found.
        """
        all_teams = teams.get_teams()
        for team in all_teams:
            if team['abbreviation'].upper() == team_abbrev.upper():
                return team['id']
        raise NBAApiError(f"Team not found: {team_abbrev}")

    def get_game_shots(
        self,
        game_id: str,
        team_id: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch all shots from a specific game.

        Args:
            game_id: NBA game ID (e.g., "0022400001").
            team_id: Optional team ID to filter shots. None for all teams.

        Returns:
            DataFrame with shot data matching our schema.

        Raises:
            GameNotFoundError: If game not found.
            NBAApiError: If API request fails.

        Example:
            >>> client = NBAApiClient()
            >>> shots = client.get_game_shots("0022400123")
            >>> kings_shots = shots[shots['team'] == 'SAC']
        """
        cache_key = f"game_shots_{game_id}_{team_id or 'all'}"

        # Try cache first
        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            df = self._api_request_with_retry(
                shotchartdetail.ShotChartDetail,
                team_id=team_id or 0,
                player_id=0,
                game_id_nullable=game_id,
                context_measure_simple='FGA',
            )
        except Exception as e:
            raise NBAApiError(f"Failed to fetch game shots: {e}")

        if df.empty:
            raise GameNotFoundError(f"No shots found for game: {game_id}")

        # Transform to our schema
        result = self._transform_shot_data(df)

        # Cache the result
        self._save_to_cache(cache_key, result)

        return result

    def get_player_shots(
        self,
        player_name: str,
        season: str = DEFAULT_SEASON,
        team_id: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch all shots for a player in a season.

        Args:
            player_name: Player name (partial match supported).
            season: NBA season (e.g., "2023-24"). Defaults to current.
            team_id: Optional team ID filter.

        Returns:
            DataFrame with shot data for the player.

        Raises:
            PlayerNotFoundError: If player not found.
            NBAApiError: If API request fails.

        Example:
            >>> client = NBAApiClient()
            >>> fox_shots = client.get_player_shots("De'Aaron Fox", "2023-24")
            >>> print(f"Fox: {len(fox_shots)} shots")
        """
        # Find player ID
        player_id = self.find_player_id(player_name)

        cache_key = f"player_shots_{player_id}_{season}_{team_id or 'all'}"

        # Try cache first
        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            df = self._api_request_with_retry(
                shotchartdetail.ShotChartDetail,
                team_id=team_id or 0,
                player_id=player_id,
                season_nullable=season,
                context_measure_simple='FGA',
            )
        except Exception as e:
            raise NBAApiError(f"Failed to fetch player shots: {e}")

        # Transform to our schema
        result = self._transform_shot_data(df)

        # Cache the result
        self._save_to_cache(cache_key, result)

        return result

    def get_team_schedule(
        self,
        team: str = KINGS_ABBREVIATION,
        season: str = DEFAULT_SEASON,
    ) -> pd.DataFrame:
        """
        Get team's game schedule for a season.

        Args:
            team: Team abbreviation (default: "SAC").
            season: NBA season (e.g., "2023-24").

        Returns:
            DataFrame with game schedule including:
            - game_id: NBA game ID
            - game_date: Date of game
            - matchup: Matchup string (e.g., "SAC vs. LAL")
            - wl: Win/Loss result
            - pts: Points scored

        Example:
            >>> client = NBAApiClient()
            >>> schedule = client.get_team_schedule("SAC", "2023-24")
            >>> recent_game = schedule.iloc[0]
        """
        team_id = self.find_team_id(team)

        cache_key = f"team_schedule_{team}_{season}"

        # Try cache first
        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            df = self._api_request_with_retry(
                leaguegamefinder.LeagueGameFinder,
                team_id_nullable=team_id,
                season_nullable=season,
            )
        except Exception as e:
            raise NBAApiError(f"Failed to fetch team schedule: {e}")

        if df.empty:
            return pd.DataFrame()

        # Select relevant columns
        columns_to_keep = ['GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'PLUS_MINUS']
        available = [c for c in columns_to_keep if c in df.columns]
        result = df[available].copy()

        # Rename columns
        result = result.rename(columns={
            'GAME_ID': 'game_id',
            'GAME_DATE': 'game_date',
            'MATCHUP': 'matchup',
            'WL': 'wl',
            'PTS': 'pts',
            'PLUS_MINUS': 'plus_minus',
        })

        # Sort by date descending (most recent first)
        if 'game_date' in result.columns:
            result = result.sort_values('game_date', ascending=False)

        # Cache the result
        self._save_to_cache(cache_key, result)

        return result

    def get_recent_kings_game(self, season: str = DEFAULT_SEASON) -> dict:
        """
        Get the most recent Kings game info.

        Args:
            season: NBA season.

        Returns:
            Dictionary with game_id, date, matchup, result.

        Example:
            >>> client = NBAApiClient()
            >>> game = client.get_recent_kings_game()
            >>> print(f"Recent game: {game['matchup']} on {game['date']}")
        """
        schedule = self.get_team_schedule("SAC", season)

        if schedule.empty:
            raise GameNotFoundError("No Kings games found for season")

        recent = schedule.iloc[0]
        return {
            'game_id': recent['game_id'],
            'date': recent.get('game_date', 'Unknown'),
            'matchup': recent.get('matchup', 'Unknown'),
            'result': recent.get('wl', 'Unknown'),
            'points': recent.get('pts', 0),
        }

    def clear_cache(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of cache files deleted.
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1

        return count
