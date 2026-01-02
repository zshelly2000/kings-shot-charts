#!/usr/bin/env python3
"""
Fetch Real Game Demo - Kings Shot Chart Generator

This script demonstrates fetching real shot data from the NBA API
and creating shot charts from it.

Usage:
    python examples/fetch_real_game_demo.py

Output:
    - Fetches recent Kings game data from NBA API
    - Creates shot charts for Kings players
    - Saves to output/real_game/
    - Compares API data to our sample data format
"""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.nba_api_client import (
    NBAApiClient,
    NBAApiError,
    PlayerNotFoundError,
    GameNotFoundError,
)
from src.data.data_loader import get_shot_summary, filter_shots
from src.visualization.shot_chart import ShotChart, create_player_shot_chart


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print('='*60)


def print_stats(name: str, df) -> None:
    """Print shooting statistics."""
    if len(df) == 0:
        print(f"  {name}: No shots")
        return
    summary = get_shot_summary(df)
    print(f"  {name}")
    print(f"    FG: {summary['made_shots']}/{summary['total_shots']} ({summary['fg_pct']:.1%})")
    if summary['two_pt_total'] > 0 or summary['three_pt_total'] > 0:
        print(f"    2PT: {summary['two_pt_made']}/{summary['two_pt_total']} | "
              f"3PT: {summary['three_pt_made']}/{summary['three_pt_total']}")


def main():
    """Run the real game demo."""
    output_dir = project_root / 'output' / 'real_game'
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("Kings Shot Chart - Real NBA API Demo")

    # =========================================================================
    # Step 1: Initialize API client
    # =========================================================================
    print("\n[1] Initializing NBA API client...")
    client = NBAApiClient(use_cache=True)
    print("    [OK] Client ready (caching enabled)")

    # =========================================================================
    # Step 2: Find player IDs
    # =========================================================================
    print_header("Looking Up Player IDs")

    players_to_find = ["De'Aaron Fox", "Domantas Sabonis", "Keegan Murray"]

    print("\n[2] Finding player IDs...")
    player_ids = {}
    for name in players_to_find:
        try:
            player_id = client.find_player_id(name)
            player_ids[name] = player_id
            print(f"    {name}: {player_id}")
        except PlayerNotFoundError as e:
            print(f"    {name}: NOT FOUND - {e}")

    # =========================================================================
    # Step 3: Get Kings schedule
    # =========================================================================
    print_header("Fetching Kings Schedule")

    print("\n[3] Fetching 2023-24 season schedule...")
    try:
        schedule = client.get_team_schedule("SAC", "2023-24")
        print(f"    [OK] Found {len(schedule)} games")

        if len(schedule) > 0:
            print("\n    Recent games:")
            for i, row in schedule.head(5).iterrows():
                result = row.get('wl', '?')
                pts = row.get('pts', '?')
                print(f"      {row['game_date']}: {row['matchup']} ({result}, {pts} pts)")
    except NBAApiError as e:
        print(f"    [ERROR] {e}")
        schedule = None

    # =========================================================================
    # Step 4: Fetch shots from a game
    # =========================================================================
    print_header("Fetching Game Shot Data")

    if schedule is not None and len(schedule) > 0:
        # Get the most recent game
        recent_game = schedule.iloc[0]
        game_id = recent_game['game_id']

        print(f"\n[4] Fetching shots from game {game_id}...")
        print(f"    Game: {recent_game['matchup']} on {recent_game['game_date']}")

        try:
            game_shots = client.get_game_shots(game_id)
            print(f"    [OK] Fetched {len(game_shots)} shots")

            # Filter to Kings shots only
            kings_shots = game_shots[game_shots['team'] == 'SAC']
            print(f"    Kings shots: {len(kings_shots)}")

            # Show data schema
            print("\n    Data columns:")
            for col in game_shots.columns:
                print(f"      - {col}: {game_shots[col].dtype}")

            # Save to CSV for inspection
            csv_path = output_dir / f"game_{game_id}_shots.csv"
            kings_shots.to_csv(csv_path, index=False)
            print(f"\n    [OK] Saved to {csv_path.name}")

        except (GameNotFoundError, NBAApiError) as e:
            print(f"    [ERROR] {e}")
            kings_shots = None
            game_shots = None
    else:
        print("\n[4] Skipping - no schedule data")
        kings_shots = None
        game_shots = None

    # =========================================================================
    # Step 5: Create shot charts from API data
    # =========================================================================
    if kings_shots is not None and len(kings_shots) > 0:
        print_header("Creating Shot Charts from API Data")

        print("\n[5] Creating team shot chart...")
        try:
            chart = ShotChart(
                kings_shots,
                title=f"Sacramento Kings\n{recent_game['matchup']} - {recent_game['game_date']}",
                use_kings_colors=True,
            )
            chart.plot()
            chart.save(output_dir / "kings_game_shots.png")
            chart.close()
            print("    [OK] Saved: real_game/kings_game_shots.png")
            print_stats("Team", kings_shots)
        except Exception as e:
            print(f"    [ERROR] {e}")

        # Create player charts
        print("\n[6] Creating player shot charts...")
        players = kings_shots['player_name'].unique()

        for player in players:
            player_shots = filter_shots(kings_shots, player_name=player)
            if len(player_shots) == 0:
                continue

            try:
                safe_name = player.replace("'", "").replace(" ", "_").lower()
                chart = ShotChart(player_shots, title=player, use_kings_colors=True)
                chart.plot()
                chart.save(output_dir / f"{safe_name}_game.png")
                chart.close()

                print(f"\n    {player}")
                print(f"      Saved: real_game/{safe_name}_game.png")
                print_stats("", player_shots)
            except Exception as e:
                print(f"    [ERROR] {player}: {e}")

    # =========================================================================
    # Step 6: Fetch season data for a player
    # =========================================================================
    print_header("Fetching Player Season Data")

    print("\n[7] Fetching De'Aaron Fox 2023-24 season shots...")
    try:
        fox_season = client.get_player_shots("De'Aaron Fox", "2023-24")
        print(f"    [OK] Fetched {len(fox_season)} shots for the season")

        # Save a subset
        csv_path = output_dir / "fox_season_shots.csv"
        fox_season.head(100).to_csv(csv_path, index=False)
        print(f"    [OK] Saved first 100 shots to {csv_path.name}")

        # Create season chart (might have many shots)
        if len(fox_season) > 0:
            chart = ShotChart(
                fox_season,
                title="De'Aaron Fox - 2023-24 Season",
                use_kings_colors=True,
                marker_size=50,  # Smaller markers for many shots
            )
            chart.plot()
            chart.save(output_dir / "fox_season.png", dpi=200)
            chart.close()
            print("    [OK] Saved: real_game/fox_season.png")
            print_stats("Season", fox_season)

    except (PlayerNotFoundError, NBAApiError) as e:
        print(f"    [ERROR] {e}")

    # =========================================================================
    # Summary
    # =========================================================================
    print_header("Demo Complete!")

    print("\n  Generated files in output/real_game/:")
    for path in sorted(output_dir.glob("*")):
        size_kb = path.stat().st_size / 1024
        print(f"    - {path.name} ({size_kb:.1f} KB)")

    print("\n  Next steps:")
    print("    - Examine the CSV files to see real NBA API data")
    print("    - Compare coordinates to our sample data")
    print("    - Note: API calls are cached in data/cache/")
    print()


if __name__ == '__main__':
    main()
