#!/usr/bin/env python3
"""
Data Loading Demo - Kings Shot Chart Generator

This script demonstrates how to load and work with shot data
from a CSV file using the data_loader module.

Usage:
    python examples/load_data_demo.py

Output:
    - Summary of loaded data
    - Player breakdown
    - Shot type analysis
    - Sample of filtered data
"""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import (
    load_shots_csv,
    filter_shots,
    get_shot_summary,
)


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print('='*60)


def print_summary(summary: dict) -> None:
    """Print shot summary in a readable format."""
    print(f"\n  Total Shots: {summary['total_shots']}")
    print(f"  Made: {summary['made_shots']} | Missed: {summary['missed_shots']}")
    print(f"  FG%: {summary['fg_pct']:.1%}")
    print()
    print(f"  2PT: {summary['two_pt_made']}/{summary['two_pt_total']} ({summary['two_pt_pct']:.1%})")
    print(f"  3PT: {summary['three_pt_made']}/{summary['three_pt_total']} ({summary['three_pt_pct']:.1%})")
    print()
    print(f"  Unique Players: {summary['unique_players']}")
    print(f"  Unique Games: {summary['unique_games']}")


def main():
    """Run the data loading demo."""
    csv_path = project_root / 'data' / 'sample_shots.csv'

    print_header("Kings Shot Chart - Data Loading Demo")

    # =========================================================================
    # Step 1: Load the CSV file
    # =========================================================================
    print("\n[*] Loading shot data from CSV...")
    print(f"    File: {csv_path}")

    try:
        df = load_shots_csv(csv_path)
        print(f"    [OK] Successfully loaded {len(df)} shots")
    except FileNotFoundError:
        print(f"    [ERROR] File not found: {csv_path}")
        return
    except Exception as e:
        print(f"    [ERROR] Loading file: {e}")
        return

    # =========================================================================
    # Step 2: Display overall summary
    # =========================================================================
    print_header("Overall Shot Summary")
    summary = get_shot_summary(df)
    print_summary(summary)

    # =========================================================================
    # Step 3: Show data types
    # =========================================================================
    print_header("Data Types")
    print("\n  Column             Type")
    print("  " + "-"*35)
    for col in df.columns:
        dtype = str(df[col].dtype)
        print(f"  {col:<20} {dtype}")

    # =========================================================================
    # Step 4: Player breakdown
    # =========================================================================
    print_header("Player Breakdown")

    players = df['player_name'].unique()
    for player in players:
        player_shots = filter_shots(df, player_name=player)
        player_summary = get_shot_summary(player_shots)
        print(f"\n  {player}")
        print(f"    Shots: {player_summary['total_shots']} | "
              f"FG: {player_summary['made_shots']}/{player_summary['total_shots']} "
              f"({player_summary['fg_pct']:.1%})")
        print(f"    2PT: {player_summary['two_pt_made']}/{player_summary['two_pt_total']} | "
              f"3PT: {player_summary['three_pt_made']}/{player_summary['three_pt_total']}")

    # =========================================================================
    # Step 5: Shot type analysis
    # =========================================================================
    print_header("Shot Type Analysis")

    two_pt = filter_shots(df, shot_type="2PT")
    three_pt = filter_shots(df, shot_type="3PT")

    print(f"\n  2-Point Shots: {len(two_pt)}")
    if len(two_pt) > 0:
        print(f"    Zones: {', '.join(two_pt['shot_zone'].unique())}")

    print(f"\n  3-Point Shots: {len(three_pt)}")
    if len(three_pt) > 0:
        print(f"    Zones: {', '.join(three_pt['shot_zone'].unique())}")

    # =========================================================================
    # Step 6: Filtering example
    # =========================================================================
    print_header("Filtering Example")

    print("\n  Filter: De'Aaron Fox's made 3-pointers")
    fox_made_threes = filter_shots(
        df,
        player_name="Fox",
        shot_type="3PT",
        made_only=True
    )

    if len(fox_made_threes) > 0:
        print(f"  Found: {len(fox_made_threes)} shots\n")
        print("  Period  Zone             Distance  Location (x, y)")
        print("  " + "-"*55)
        for _, shot in fox_made_threes.iterrows():
            print(f"  Q{shot['period']:<6} {shot['shot_zone']:<16} "
                  f"{shot['shot_distance']:>5.1f} ft   "
                  f"({shot['loc_x']:>4.0f}, {shot['loc_y']:>4.0f})")
    else:
        print("  No shots found matching criteria")

    # =========================================================================
    # Step 7: Sample data preview
    # =========================================================================
    print_header("Sample Data (First 5 Rows)")
    print()
    # Show subset of columns for readability
    preview_cols = ['player_name', 'period', 'shot_made', 'shot_type', 'shot_zone', 'loc_x', 'loc_y']
    print(df[preview_cols].head().to_string(index=False))

    print_header("Demo Complete")
    print("\n  Next steps:")
    print("  - Use this data with the CourtDrawer to create shot charts")
    print("  - Try different filters to analyze specific scenarios")
    print("  - Load your own CSV data with the same column structure\n")


if __name__ == '__main__':
    main()
