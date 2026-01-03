# Usage Guide

Detailed documentation for the Kings Shot Chart Generator.

## Table of Contents

- [Quick Start](#quick-start)
- [Loading Data](#loading-data)
- [Creating Shot Charts](#creating-shot-charts)
- [NBA API Integration](#nba-api-integration)
- [API Reference](#api-reference)

---

## Quick Start

```python
from src.data.data_loader import load_shots_csv
from src.visualization.shot_chart import ShotChart

# Load data and create chart
shots = load_shots_csv("data/sample_shots.csv")
chart = ShotChart(shots, title="Kings Shots", use_kings_colors=True)
chart.plot()
chart.save("output/chart.png")
chart.close()
```

---

## Loading Data

### From CSV Files

```python
from src.data.data_loader import load_shots_csv, filter_shots, get_shot_summary

# Load shots
shots = load_shots_csv("data/sample_shots.csv")

# Filter by player
fox_shots = filter_shots(shots, player_name="De'Aaron Fox")

# Filter by multiple criteria
q4_shots = filter_shots(shots, period=4, shot_made=True)

# Get statistics
summary = get_shot_summary(fox_shots)
print(f"FG%: {summary['fg_pct']:.1%}")
print(f"3PT: {summary['three_pt_made']}/{summary['three_pt_total']}")
```

### CSV Format

Required columns:
| Column | Type | Description |
|--------|------|-------------|
| `loc_x` | float | X coordinate (-250 to 250) |
| `loc_y` | float | Y coordinate (0 to ~470) |
| `shot_made` | bool | True if made, False if missed |

Optional columns: `player_name`, `team`, `period`, `shot_type`, `shot_distance`, `action_type`

---

## Creating Shot Charts

### Basic Chart

```python
from src.visualization.shot_chart import ShotChart

chart = ShotChart(shots_df)
chart.plot()
chart.show()  # Display interactively
```

### Customized Chart

```python
chart = ShotChart(
    shots_df,
    title="De'Aaron Fox - Season Stats",
    use_kings_colors=True,    # Purple/gray theme
    marker_size=100,          # Shot marker size
    show_legend=True,
    figsize=(12, 11),
)
chart.plot()
chart.save("fox_chart.png", dpi=150)
chart.close()
```

### Multiple Charts

```python
from src.visualization.shot_chart import create_player_shot_chart

# Quick single-player chart
fig, ax = create_player_shot_chart(
    shots_df,
    player_name="Domantas Sabonis",
    title="Sabonis Shot Chart"
)
fig.savefig("sabonis.png")
```

---

## NBA API Integration

### Initialize Client

```python
from src.data.nba_api_client import NBAApiClient

# With caching (recommended)
client = NBAApiClient(use_cache=True)

# Without caching
client = NBAApiClient(use_cache=False)

# Custom cache location
client = NBAApiClient(cache_dir="my_cache/")
```

### Fetch Game Data

```python
# Get recent Kings game
game = client.get_recent_kings_game()
print(f"Game: {game['matchup']} on {game['date']}")

# Get shots from a specific game
shots = client.get_game_shots(game['game_id'])
kings_shots = shots[shots['team'] == 'SAC']
```

### Fetch Player Data

```python
# Get player's season shots
fox_shots = client.get_player_shots("De'Aaron Fox", "2023-24")

# Find player ID
player_id = client.find_player_id("Keegan Murray")
```

### Fetch Team Schedule

```python
# Get Kings schedule
schedule = client.get_team_schedule("SAC", "2023-24")

# Most recent games
for _, game in schedule.head(5).iterrows():
    print(f"{game['game_date']}: {game['matchup']} ({game['wl']})")
```

### Cache Management

```python
# Clear all cached data
deleted = client.clear_cache()
print(f"Cleared {deleted} cached files")
```

---

## API Reference

### ShotChart

```python
class ShotChart:
    def __init__(
        self,
        shots_df: pd.DataFrame,      # Shot data with loc_x, loc_y, shot_made
        title: str = "",             # Chart title
        use_kings_colors: bool = False,
        marker_size: int = 100,
        show_legend: bool = True,
        figsize: tuple = (12, 11),
    )

    def plot(self) -> None           # Render the chart
    def save(self, path, dpi=150)    # Save to file
    def show(self) -> None           # Display interactively
    def close(self) -> None          # Close figure (free memory)
    def get_figure(self) -> Figure   # Get matplotlib Figure
```

### NBAApiClient

```python
class NBAApiClient:
    def __init__(
        self,
        cache_dir: Path = None,      # Cache directory
        use_cache: bool = True,
        request_delay: float = 0.6,  # Rate limiting
    )

    def find_player_id(name: str) -> int
    def find_team_id(abbrev: str) -> int
    def get_game_shots(game_id: str, team_id: int = None) -> DataFrame
    def get_player_shots(name: str, season: str) -> DataFrame
    def get_team_schedule(team: str, season: str) -> DataFrame
    def get_recent_kings_game(season: str) -> dict
    def clear_cache() -> int
```

### Data Loader Functions

```python
def load_shots_csv(filepath: str) -> pd.DataFrame
def filter_shots(
    df: pd.DataFrame,
    player_name: str = None,
    team: str = None,
    period: int = None,
    shot_made: bool = None,
    shot_type: str = None,
) -> pd.DataFrame
def get_shot_summary(df: pd.DataFrame) -> dict
```

### Exceptions

```python
from src.data.nba_api_client import (
    NBAApiError,          # Base API error
    PlayerNotFoundError,  # Player lookup failed
    GameNotFoundError,    # Game not found
    RateLimitError,       # API rate limit hit
)

from src.data.data_loader import (
    DataValidationError,  # Base validation error
    MissingColumnsError,  # Required columns missing
    InvalidDataTypeError, # Type conversion failed
)
```

---

## Tips

1. **Use caching** - NBA API has rate limits; caching avoids redundant requests
2. **Close charts** - Call `chart.close()` when done to free memory
3. **Filter early** - Filter large datasets before plotting for better performance
4. **Check coordinates** - NBA API uses X: -250 to 250, Y: 0 to ~470
