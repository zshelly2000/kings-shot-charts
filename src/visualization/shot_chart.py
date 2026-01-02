"""
Shot Chart Module for Kings Shot Chart Generator.

This module provides the ShotChart class for creating visual shot charts
by combining court drawings with shot data from the NBA API.

Example:
    >>> from src.visualization.shot_chart import ShotChart
    >>> from src.data.data_loader import load_shots_csv
    >>>
    >>> df = load_shots_csv('data/sample_shots.csv')
    >>> chart = ShotChart(df, title="De'Aaron Fox")
    >>> chart.plot()
    >>> chart.save('output/fox_shots.png')
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import pandas as pd

from src.visualization.court import CourtDrawer
from src.data.data_loader import filter_shots, get_shot_summary
from src.utils.config import (
    DEFAULT_FIGURE_SIZE,
    MADE_SHOT_COLOR,
    MISSED_SHOT_COLOR,
    MADE_SHOT_COLOR_ALT,
    MISSED_SHOT_COLOR_ALT,
    SHOT_MARKER_SIZE,
    SHOT_MARKER_ALPHA,
    KINGS_PURPLE,
)


class ShotChart:
    """
    Creates visual shot charts by plotting shot data on an NBA court.

    The ShotChart class combines shot location data with a court drawing
    to create informative visualizations of shooting performance.

    Attributes:
        shots_df: DataFrame containing shot data with loc_x, loc_y columns.
        title: Optional title for the chart.
        made_color: Color for made shots (default: Kings purple).
        missed_color: Color for missed shots (default: gray).
        marker_size: Size of shot markers (default: 200).

    Example:
        >>> df = load_shots_csv('data/sample_shots.csv')
        >>> chart = ShotChart(df, title="Sacramento Kings")
        >>> chart.plot()
        >>> chart.save('kings_shots.png')
    """

    def __init__(
        self,
        shots_df: pd.DataFrame,
        title: Optional[str] = None,
        made_color: str = MADE_SHOT_COLOR_ALT,  # Green by default
        missed_color: str = MISSED_SHOT_COLOR_ALT,  # Red by default
        marker_size: int = SHOT_MARKER_SIZE,
        fig_size: Tuple[float, float] = DEFAULT_FIGURE_SIZE,
        use_kings_colors: bool = False,
    ) -> None:
        """
        Initialize a ShotChart with shot data.

        Args:
            shots_df: DataFrame with shot data (must have loc_x, loc_y, shot_made).
            title: Title to display on the chart.
            made_color: Color for made shot markers.
            missed_color: Color for missed shot markers.
            marker_size: Size of shot markers (default: 200).
            fig_size: Figure size as (width, height) in inches.
            use_kings_colors: If True, use Kings purple/gray color scheme.
        """
        self.shots_df = shots_df.copy()
        self.title = title
        self.marker_size = marker_size
        self.fig_size = fig_size

        # Set colors based on theme
        if use_kings_colors:
            self.made_color = MADE_SHOT_COLOR  # Kings purple
            self.missed_color = MISSED_SHOT_COLOR  # Gray
        else:
            self.made_color = made_color
            self.missed_color = missed_color

        # Initialize court drawer
        self.court_drawer = CourtDrawer(fig_size=fig_size)

        # Store figure and axes for later use
        self._fig: Optional[Figure] = None
        self._ax: Optional[Axes] = None

    def _validate_data(self) -> None:
        """
        Validate that the DataFrame has required columns.

        Raises:
            ValueError: If required columns are missing.
        """
        required = ['loc_x', 'loc_y', 'shot_made']
        missing = [col for col in required if col not in self.shots_df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _get_title_with_stats(self) -> str:
        """
        Generate a title string with shooting statistics.

        Returns:
            Formatted title string with FG stats.
        """
        summary = get_shot_summary(self.shots_df)
        total = summary['total_shots']
        made = summary['made_shots']
        pct = summary['fg_pct']

        base_title = self.title or "Shot Chart"
        return f"{base_title}\nFG: {made}/{total} ({pct:.1%})"

    def _add_legend(self, ax: Axes) -> None:
        """
        Add a legend showing made/missed counts.

        Args:
            ax: Matplotlib axes to add legend to.
        """
        summary = get_shot_summary(self.shots_df)
        made_count = summary['made_shots']
        missed_count = summary['missed_shots']

        # Create legend handles
        made_handle = ax.scatter(
            [], [], c=self.made_color, s=self.marker_size,
            marker='o', label=f'Made: {made_count}',
            alpha=SHOT_MARKER_ALPHA, edgecolors='black', linewidths=0.5
        )
        missed_handle = ax.scatter(
            [], [], c=self.missed_color, s=self.marker_size,
            marker='X', label=f'Missed: {missed_count}',
            alpha=SHOT_MARKER_ALPHA, edgecolors='black', linewidths=0.5
        )

        ax.legend(
            handles=[made_handle, missed_handle],
            loc='upper right',
            fontsize=10,
            framealpha=0.9,
            edgecolor='gray',
        )

    def _add_shot_breakdown(self, ax: Axes) -> None:
        """
        Add 2PT/3PT breakdown text to the chart.

        Args:
            ax: Matplotlib axes to add text to.
        """
        summary = get_shot_summary(self.shots_df)

        # Build breakdown text
        breakdown_lines = []
        if summary['two_pt_total'] > 0:
            breakdown_lines.append(
                f"2PT: {summary['two_pt_made']}/{summary['two_pt_total']} "
                f"({summary['two_pt_pct']:.1%})"
            )
        if summary['three_pt_total'] > 0:
            breakdown_lines.append(
                f"3PT: {summary['three_pt_made']}/{summary['three_pt_total']} "
                f"({summary['three_pt_pct']:.1%})"
            )

        if breakdown_lines:
            breakdown_text = "  |  ".join(breakdown_lines)
            # Get current y limits to position text below the visible area
            ylim = ax.get_ylim()
            text_y = ylim[0] - 10
            ax.text(
                0, text_y,
                breakdown_text,
                ha='center', va='top',
                fontsize=10,
                color='#444444',
                style='italic',
            )

    def _adjust_axis_limits(self, ax: Axes, margin: float = 30.0) -> None:
        """
        Adjust axis limits to ensure all shots are visible.

        Expands the current axis limits if any shots fall outside
        the default court boundaries.

        Args:
            ax: Matplotlib axes to adjust.
            margin: Extra margin around shots in coordinate units.
        """
        # Get current limits (set by court drawer)
        xlim = list(ax.get_xlim())
        ylim = list(ax.get_ylim())

        # Get shot coordinate ranges
        x_min = self.shots_df['loc_x'].min()
        x_max = self.shots_df['loc_x'].max()
        y_min = self.shots_df['loc_y'].min()
        y_max = self.shots_df['loc_y'].max()

        # Expand limits if shots fall outside
        if x_min - margin < xlim[0]:
            xlim[0] = x_min - margin
        if x_max + margin > xlim[1]:
            xlim[1] = x_max + margin
        if y_min - margin < ylim[0]:
            ylim[0] = y_min - margin
        if y_max + margin > ylim[1]:
            ylim[1] = y_max + margin

        # Apply adjusted limits
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    def plot(
        self,
        ax: Optional[Axes] = None,
        show_legend: bool = True,
        show_title: bool = True,
        show_breakdown: bool = True,
    ) -> Tuple[Figure, Axes]:
        """
        Create the shot chart visualization.

        Draws the court, plots all shots with color coding based on
        whether they were made or missed, and adds labels/legend.

        Args:
            ax: Optional matplotlib axes to draw on. Creates new if None.
            show_legend: If True, add legend with made/missed counts.
            show_title: If True, add title with statistics.
            show_breakdown: If True, add 2PT/3PT breakdown below chart.

        Returns:
            Tuple of (Figure, Axes) with the shot chart.

        Example:
            >>> chart = ShotChart(df)
            >>> fig, ax = chart.plot()
            >>> plt.show()
        """
        self._validate_data()

        # Create figure and draw court
        if ax is None:
            self._fig, self._ax = plt.subplots(figsize=self.fig_size)
            ax = self._ax
        else:
            self._ax = ax
            self._fig = ax.get_figure()

        # Draw the court
        self.court_drawer.draw_court(ax)

        # Separate made and missed shots
        made_shots = self.shots_df[self.shots_df['shot_made'] == True]
        missed_shots = self.shots_df[self.shots_df['shot_made'] == False]

        # Plot made shots (circles)
        if len(made_shots) > 0:
            ax.scatter(
                made_shots['loc_x'],
                made_shots['loc_y'],
                c=self.made_color,
                s=self.marker_size,
                marker='o',
                alpha=SHOT_MARKER_ALPHA,
                edgecolors='black',
                linewidths=0.5,
                zorder=3,
                label='Made'
            )

        # Plot missed shots (X markers)
        if len(missed_shots) > 0:
            ax.scatter(
                missed_shots['loc_x'],
                missed_shots['loc_y'],
                c=self.missed_color,
                s=self.marker_size,
                marker='X',
                alpha=SHOT_MARKER_ALPHA,
                edgecolors='black',
                linewidths=0.5,
                zorder=3,
                label='Missed'
            )

        # Adjust axis limits to ensure all shots are visible
        self._adjust_axis_limits(ax)

        # Add title with stats
        if show_title:
            title_text = self._get_title_with_stats()
            ax.set_title(
                title_text,
                fontsize=14,
                fontweight='bold',
                color='#333333',
                pad=10,
            )

        # Add legend
        if show_legend:
            self._add_legend(ax)

        # Add shot breakdown
        if show_breakdown:
            self._add_shot_breakdown(ax)

        return self._fig, ax

    def save(
        self,
        filepath: Union[str, Path],
        dpi: int = 150,
        bbox_inches: str = 'tight',
        facecolor: str = 'white',
        **kwargs
    ) -> None:
        """
        Save the shot chart to a file.

        Args:
            filepath: Path to save the image to.
            dpi: Resolution in dots per inch (default: 150).
            bbox_inches: Bounding box setting (default: 'tight').
            facecolor: Background color (default: 'white').
            **kwargs: Additional arguments passed to plt.savefig().

        Raises:
            RuntimeError: If plot() hasn't been called yet.

        Example:
            >>> chart = ShotChart(df)
            >>> chart.plot()
            >>> chart.save('output/shot_chart.png', dpi=300)
        """
        if self._fig is None:
            # Auto-plot if not done yet
            self.plot()

        filepath = Path(filepath)

        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        self._fig.savefig(
            filepath,
            dpi=dpi,
            bbox_inches=bbox_inches,
            facecolor=facecolor,
            **kwargs
        )

    def show(self) -> None:
        """
        Display the shot chart in a window.

        Calls plot() if not already done, then shows the figure.

        Example:
            >>> chart = ShotChart(df)
            >>> chart.show()  # Opens matplotlib window
        """
        if self._fig is None:
            self.plot()

        plt.show()

    def close(self) -> None:
        """
        Close the figure to free memory.

        Should be called after saving when creating multiple charts.
        """
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
            self._ax = None


def create_player_shot_chart(
    shots_df: pd.DataFrame,
    player_name: str,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> ShotChart:
    """
    Convenience function to create a shot chart for a specific player.

    Args:
        shots_df: DataFrame with all shot data.
        player_name: Name of player to filter for (partial match).
        output_path: If provided, save chart to this path.
        **kwargs: Additional arguments passed to ShotChart.

    Returns:
        ShotChart instance with player's shots.

    Example:
        >>> df = load_shots_csv('data/sample_shots.csv')
        >>> chart = create_player_shot_chart(df, "Fox", "output/fox.png")
    """
    player_shots = filter_shots(shots_df, player_name=player_name)

    if len(player_shots) == 0:
        raise ValueError(f"No shots found for player: {player_name}")

    # Get full player name for title
    full_name = player_shots['player_name'].iloc[0]

    chart = ShotChart(player_shots, title=full_name, **kwargs)
    chart.plot()

    if output_path:
        chart.save(output_path)

    return chart


def create_team_shot_chart(
    shots_df: pd.DataFrame,
    team: Optional[str] = None,
    title: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> ShotChart:
    """
    Convenience function to create a team shot chart.

    Args:
        shots_df: DataFrame with shot data.
        team: Team abbreviation to filter (e.g., 'SAC'). None for all.
        title: Chart title. Defaults to team name or "Team Shot Chart".
        output_path: If provided, save chart to this path.
        **kwargs: Additional arguments passed to ShotChart.

    Returns:
        ShotChart instance with team's shots.

    Example:
        >>> df = load_shots_csv('data/sample_shots.csv')
        >>> chart = create_team_shot_chart(df, team="SAC", output_path="output/kings.png")
    """
    if team:
        team_shots = filter_shots(shots_df, team=team)
        chart_title = title or f"{team} Shot Chart"
    else:
        team_shots = shots_df
        chart_title = title or "Shot Chart"

    if len(team_shots) == 0:
        raise ValueError(f"No shots found for team: {team}")

    chart = ShotChart(team_shots, title=chart_title, **kwargs)
    chart.plot()

    if output_path:
        chart.save(output_path)

    return chart
