#!/usr/bin/env python3
"""
Shot Chart Demo - Kings Shot Chart Generator

This script demonstrates how to create shot chart visualizations
by combining the data loader and visualization modules.

Usage:
    python examples/create_shot_chart_demo.py

Output:
    - Individual player shot charts saved to output/
    - Team shot chart saved to output/
    - 3-point only shot chart saved to output/
"""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import load_shots_csv, filter_shots, get_shot_summary
from src.visualization.shot_chart import (
    ShotChart,
    create_player_shot_chart,
    create_team_shot_chart,
)


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print('='*60)


def print_stats(name: str, df) -> None:
    """Print shooting statistics for a dataset."""
    summary = get_shot_summary(df)
    print(f"  {name}")
    print(f"    FG: {summary['made_shots']}/{summary['total_shots']} ({summary['fg_pct']:.1%})")
    print(f"    2PT: {summary['two_pt_made']}/{summary['two_pt_total']} | "
          f"3PT: {summary['three_pt_made']}/{summary['three_pt_total']}")


def main():
    """Run the shot chart demo."""
    csv_path = project_root / 'data' / 'sample_shots.csv'
    output_dir = project_root / 'output'

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("Kings Shot Chart Generator - Demo")

    # =========================================================================
    # Step 1: Load the data
    # =========================================================================
    print("\n[1] Loading shot data...")
    print(f"    File: {csv_path}")

    try:
        df = load_shots_csv(csv_path)
        print(f"    [OK] Loaded {len(df)} shots")
    except Exception as e:
        print(f"    [ERROR] {e}")
        return

    # =========================================================================
    # Step 2: Create team shot chart
    # =========================================================================
    print_header("Creating Team Shot Chart")

    print("\n[2] Creating Sacramento Kings team shot chart...")
    team_chart = create_team_shot_chart(
        df,
        team="SAC",
        title="Sacramento Kings",
        use_kings_colors=True,
        output_path=output_dir / "kings_all_shots.png"
    )
    print(f"    [OK] Saved to: output/kings_all_shots.png")
    print_stats("Team Stats:", df)
    team_chart.close()

    # =========================================================================
    # Step 3: Create individual player charts
    # =========================================================================
    print_header("Creating Player Shot Charts")

    players = df['player_name'].unique()
    print(f"\n[3] Creating charts for {len(players)} players...")

    for player in players:
        player_shots = filter_shots(df, player_name=player)

        # Create safe filename
        safe_name = player.replace("'", "").replace(" ", "_").lower()
        output_path = output_dir / f"{safe_name}_shots.png"

        # Create and save chart
        chart = ShotChart(
            player_shots,
            title=player,
            use_kings_colors=True,
        )
        chart.plot()
        chart.save(output_path)
        chart.close()

        print(f"\n    {player}")
        print(f"    Saved: output/{safe_name}_shots.png")
        print_stats("", player_shots)

    # =========================================================================
    # Step 4: Create filtered charts (3-pointers only)
    # =========================================================================
    print_header("Creating Filtered Shot Charts")

    print("\n[4] Creating 3-point shots only chart...")
    three_pt_shots = filter_shots(df, shot_type="3PT")

    chart = ShotChart(
        three_pt_shots,
        title="Sacramento Kings - 3PT Attempts",
    )
    chart.plot()
    chart.save(output_dir / "kings_3pt_only.png")
    chart.close()

    print(f"    [OK] Saved to: output/kings_3pt_only.png")
    print_stats("3PT Stats:", three_pt_shots)

    # =========================================================================
    # Step 5: Create made shots only chart
    # =========================================================================
    print("\n[5] Creating made shots only chart...")
    made_shots = filter_shots(df, made_only=True)

    chart = ShotChart(
        made_shots,
        title="Sacramento Kings - Made Shots",
        made_color='#228B22',  # Forest green
    )
    chart.plot()
    chart.save(output_dir / "kings_made_shots.png")
    chart.close()

    print(f"    [OK] Saved to: output/kings_made_shots.png")
    print(f"    Made shots: {len(made_shots)}")

    # =========================================================================
    # Step 6: Create missed shots only chart
    # =========================================================================
    print("\n[6] Creating missed shots only chart...")
    missed_shots = filter_shots(df, made_only=False)

    chart = ShotChart(
        missed_shots,
        title="Sacramento Kings - Missed Shots",
        missed_color='#DC143C',  # Crimson
    )
    chart.plot()
    chart.save(output_dir / "kings_missed_shots.png")
    chart.close()

    print(f"    [OK] Saved to: output/kings_missed_shots.png")
    print(f"    Missed shots: {len(missed_shots)}")

    # =========================================================================
    # Summary
    # =========================================================================
    print_header("Demo Complete!")

    print("\n  Generated files in output/:")
    for path in sorted(output_dir.glob("*.png")):
        print(f"    - {path.name}")

    print("\n  Usage examples:")
    print("    from src.visualization import ShotChart, create_player_shot_chart")
    print("    from src.data import load_shots_csv, filter_shots")
    print()
    print("    df = load_shots_csv('data/sample_shots.csv')")
    print("    chart = create_player_shot_chart(df, 'Fox', 'output/fox.png')")
    print()


if __name__ == '__main__':
    main()
