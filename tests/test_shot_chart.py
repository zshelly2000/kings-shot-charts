"""
Unit tests for the shot chart module.

Tests verify that:
1. ShotChart class initializes correctly
2. Shot data is plotted properly
3. Made/missed shots have correct styling
4. Titles and legends are added
5. Charts can be saved to files
6. Convenience functions work correctly
"""

import pytest
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path

from src.visualization.shot_chart import (
    ShotChart,
    create_player_shot_chart,
    create_team_shot_chart,
)
from src.data.data_loader import load_shots_csv, filter_shots
from src.utils.config import (
    MADE_SHOT_COLOR_ALT,
    MISSED_SHOT_COLOR_ALT,
    MADE_SHOT_COLOR,
    MISSED_SHOT_COLOR,
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
def minimal_shot_data():
    """Create minimal valid shot DataFrame for testing."""
    return pd.DataFrame({
        'game_id': ['001', '001', '001', '001'],
        'player_id': [1, 1, 2, 2],
        'player_name': ['Player A', 'Player A', 'Player B', 'Player B'],
        'team': ['SAC', 'SAC', 'SAC', 'SAC'],
        'period': [1, 1, 2, 2],
        'minutes_remaining': [10, 8, 6, 4],
        'seconds_remaining': [30, 15, 45, 20],
        'shot_made': [True, False, True, False],
        'shot_type': ['2PT Field Goal', '3PT Field Goal', '2PT Field Goal', '3PT Field Goal'],
        'shot_distance': [5.0, 24.0, 8.0, 25.0],
        'loc_x': [10, -180, 50, 200],
        'loc_y': [20, 90, 100, 85],
        'shot_zone': ['Paint', 'Left Wing 3', 'Mid-Range', 'Right Wing 3'],
        'action_type': ['Layup', 'Jump Shot', 'Pull-Up', 'Jump Shot'],
    })


@pytest.fixture
def fox_shots(sample_df):
    """Get De'Aaron Fox shots from sample data."""
    return filter_shots(sample_df, player_name="Fox")


# =============================================================================
# Test ShotChart Initialization
# =============================================================================

class TestShotChartInit:
    """Test ShotChart class initialization."""

    def test_init_with_dataframe(self, minimal_shot_data):
        """Can initialize with DataFrame."""
        chart = ShotChart(minimal_shot_data)
        assert chart.shots_df is not None
        assert len(chart.shots_df) == 4

    def test_init_with_title(self, minimal_shot_data):
        """Can set title on initialization."""
        chart = ShotChart(minimal_shot_data, title="Test Chart")
        assert chart.title == "Test Chart"

    def test_init_default_colors(self, minimal_shot_data):
        """Default colors are green/red."""
        chart = ShotChart(minimal_shot_data)
        assert chart.made_color == MADE_SHOT_COLOR_ALT  # Green
        assert chart.missed_color == MISSED_SHOT_COLOR_ALT  # Red

    def test_init_kings_colors(self, minimal_shot_data):
        """Kings colors can be enabled."""
        chart = ShotChart(minimal_shot_data, use_kings_colors=True)
        assert chart.made_color == MADE_SHOT_COLOR  # Kings purple
        assert chart.missed_color == MISSED_SHOT_COLOR  # Gray

    def test_init_custom_colors(self, minimal_shot_data):
        """Custom colors can be set."""
        chart = ShotChart(
            minimal_shot_data,
            made_color='blue',
            missed_color='orange'
        )
        assert chart.made_color == 'blue'
        assert chart.missed_color == 'orange'

    def test_init_custom_marker_size(self, minimal_shot_data):
        """Custom marker size can be set."""
        chart = ShotChart(minimal_shot_data, marker_size=300)
        assert chart.marker_size == 300

    def test_init_copies_dataframe(self, minimal_shot_data):
        """DataFrame is copied, not referenced."""
        chart = ShotChart(minimal_shot_data)
        # Modify original
        minimal_shot_data.loc[0, 'shot_made'] = False
        # Chart data should be unchanged
        assert chart.shots_df.loc[0, 'shot_made'] == True


# =============================================================================
# Test Data Validation
# =============================================================================

class TestDataValidation:
    """Test data validation in ShotChart."""

    def test_missing_loc_x_raises(self, minimal_shot_data):
        """Missing loc_x column raises ValueError."""
        df = minimal_shot_data.drop(columns=['loc_x'])
        chart = ShotChart(df)
        with pytest.raises(ValueError) as exc_info:
            chart.plot()
        assert 'loc_x' in str(exc_info.value)

    def test_missing_loc_y_raises(self, minimal_shot_data):
        """Missing loc_y column raises ValueError."""
        df = minimal_shot_data.drop(columns=['loc_y'])
        chart = ShotChart(df)
        with pytest.raises(ValueError) as exc_info:
            chart.plot()
        assert 'loc_y' in str(exc_info.value)

    def test_missing_shot_made_raises(self, minimal_shot_data):
        """Missing shot_made column raises ValueError."""
        df = minimal_shot_data.drop(columns=['shot_made'])
        chart = ShotChart(df)
        with pytest.raises(ValueError) as exc_info:
            chart.plot()
        assert 'shot_made' in str(exc_info.value)


# =============================================================================
# Test Plot Method
# =============================================================================

class TestPlotMethod:
    """Test the plot() method."""

    def test_plot_returns_figure_and_axes(self, minimal_shot_data):
        """plot() returns (Figure, Axes) tuple."""
        chart = ShotChart(minimal_shot_data)
        result = chart.plot()

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Figure)
        assert isinstance(result[1], Axes)
        plt.close(result[0])

    def test_plot_creates_internal_figure(self, minimal_shot_data):
        """plot() creates internal figure reference."""
        chart = ShotChart(minimal_shot_data)
        assert chart._fig is None

        chart.plot()
        assert chart._fig is not None
        assert chart._ax is not None
        plt.close(chart._fig)

    def test_plot_with_existing_axes(self, minimal_shot_data):
        """Can plot on existing axes."""
        fig, ax = plt.subplots()
        chart = ShotChart(minimal_shot_data)
        returned_fig, returned_ax = chart.plot(ax=ax)

        assert returned_ax is ax
        plt.close(fig)

    def test_plot_adds_title(self, minimal_shot_data):
        """Plot adds title with statistics."""
        chart = ShotChart(minimal_shot_data, title="Test Player")
        fig, ax = chart.plot()

        title = ax.get_title()
        assert "Test Player" in title
        assert "FG:" in title
        assert "2/4" in title  # 2 made out of 4
        assert "50.0%" in title
        plt.close(fig)

    def test_plot_without_title(self, minimal_shot_data):
        """Can hide title."""
        chart = ShotChart(minimal_shot_data)
        fig, ax = chart.plot(show_title=False)

        title = ax.get_title()
        assert title == ""
        plt.close(fig)

    def test_plot_adds_legend(self, minimal_shot_data):
        """Plot adds legend with counts."""
        chart = ShotChart(minimal_shot_data)
        fig, ax = chart.plot()

        legend = ax.get_legend()
        assert legend is not None
        plt.close(fig)

    def test_plot_without_legend(self, minimal_shot_data):
        """Can hide legend."""
        chart = ShotChart(minimal_shot_data)
        fig, ax = chart.plot(show_legend=False)

        legend = ax.get_legend()
        assert legend is None
        plt.close(fig)

    def test_plot_has_scatter_collections(self, minimal_shot_data):
        """Plot creates scatter plot collections."""
        chart = ShotChart(minimal_shot_data)
        fig, ax = chart.plot(show_legend=False)

        # Should have scatter collections for shots
        collections = ax.collections
        assert len(collections) > 0
        plt.close(fig)

    def test_plot_all_made_shots(self, minimal_shot_data):
        """Can plot when all shots are made."""
        minimal_shot_data['shot_made'] = True
        chart = ShotChart(minimal_shot_data)

        # Should not raise
        fig, ax = chart.plot()
        plt.close(fig)

    def test_plot_all_missed_shots(self, minimal_shot_data):
        """Can plot when all shots are missed."""
        minimal_shot_data['shot_made'] = False
        chart = ShotChart(minimal_shot_data)

        # Should not raise
        fig, ax = chart.plot()
        plt.close(fig)


# =============================================================================
# Test Save Method
# =============================================================================

class TestSaveMethod:
    """Test the save() method."""

    def test_save_creates_file(self, minimal_shot_data, tmp_path):
        """save() creates image file."""
        chart = ShotChart(minimal_shot_data)
        chart.plot()

        output_path = tmp_path / "test_chart.png"
        chart.save(output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        plt.close(chart._fig)

    def test_save_creates_directory(self, minimal_shot_data, tmp_path):
        """save() creates parent directory if needed."""
        chart = ShotChart(minimal_shot_data)
        chart.plot()

        output_path = tmp_path / "subdir" / "test_chart.png"
        chart.save(output_path)

        assert output_path.exists()
        plt.close(chart._fig)

    def test_save_auto_plots(self, minimal_shot_data, tmp_path):
        """save() auto-calls plot() if not done."""
        chart = ShotChart(minimal_shot_data)
        # Don't call plot() first

        output_path = tmp_path / "test_chart.png"
        chart.save(output_path)

        assert output_path.exists()
        plt.close(chart._fig)

    def test_save_with_custom_dpi(self, minimal_shot_data, tmp_path):
        """save() accepts custom DPI."""
        chart = ShotChart(minimal_shot_data)
        chart.plot()

        output_low = tmp_path / "low_dpi.png"
        output_high = tmp_path / "high_dpi.png"

        chart.save(output_low, dpi=72)
        chart.save(output_high, dpi=300)

        # Higher DPI should produce larger file
        assert output_high.stat().st_size > output_low.stat().st_size
        plt.close(chart._fig)

    def test_save_multiple_formats(self, minimal_shot_data, tmp_path):
        """Can save as different formats."""
        chart = ShotChart(minimal_shot_data)
        chart.plot()

        for ext in ['.png', '.pdf', '.svg']:
            output_path = tmp_path / f"test_chart{ext}"
            chart.save(output_path)
            assert output_path.exists()

        plt.close(chart._fig)


# =============================================================================
# Test Show and Close Methods
# =============================================================================

class TestShowAndClose:
    """Test show() and close() methods."""

    def test_show_auto_plots(self, minimal_shot_data, monkeypatch):
        """show() auto-calls plot() if needed."""
        chart = ShotChart(minimal_shot_data)

        # Mock plt.show to avoid opening window
        monkeypatch.setattr(plt, 'show', lambda: None)

        chart.show()
        assert chart._fig is not None
        plt.close(chart._fig)

    def test_close_clears_figure(self, minimal_shot_data):
        """close() clears internal references."""
        chart = ShotChart(minimal_shot_data)
        chart.plot()

        assert chart._fig is not None
        chart.close()
        assert chart._fig is None
        assert chart._ax is None


# =============================================================================
# Test Convenience Functions
# =============================================================================

class TestCreatePlayerShotChart:
    """Test create_player_shot_chart function."""

    def test_creates_chart_for_player(self, sample_df):
        """Creates chart filtered to player."""
        chart = create_player_shot_chart(sample_df, "Fox")

        assert chart.title == "De'Aaron Fox"
        assert len(chart.shots_df) > 0
        assert all(chart.shots_df['player_name'].str.contains("Fox"))
        plt.close(chart._fig)

    def test_saves_to_path(self, sample_df, tmp_path):
        """Saves chart to specified path."""
        output_path = tmp_path / "fox_chart.png"
        chart = create_player_shot_chart(sample_df, "Fox", output_path)

        assert output_path.exists()
        plt.close(chart._fig)

    def test_raises_for_unknown_player(self, sample_df):
        """Raises ValueError for unknown player."""
        with pytest.raises(ValueError) as exc_info:
            create_player_shot_chart(sample_df, "Unknown Player")
        assert "No shots found" in str(exc_info.value)

    def test_passes_kwargs(self, sample_df):
        """Passes kwargs to ShotChart."""
        chart = create_player_shot_chart(
            sample_df, "Fox", use_kings_colors=True
        )
        assert chart.made_color == MADE_SHOT_COLOR
        plt.close(chart._fig)


class TestCreateTeamShotChart:
    """Test create_team_shot_chart function."""

    def test_creates_chart_for_team(self, sample_df):
        """Creates chart filtered to team."""
        chart = create_team_shot_chart(sample_df, team="SAC")

        assert "SAC" in chart.title
        assert len(chart.shots_df) == len(sample_df)
        plt.close(chart._fig)

    def test_creates_chart_all_shots(self, sample_df):
        """Creates chart for all shots when no team specified."""
        chart = create_team_shot_chart(sample_df, title="All Shots")

        assert chart.title == "All Shots"
        assert len(chart.shots_df) == len(sample_df)
        plt.close(chart._fig)

    def test_saves_to_path(self, sample_df, tmp_path):
        """Saves chart to specified path."""
        output_path = tmp_path / "team_chart.png"
        chart = create_team_shot_chart(sample_df, output_path=output_path)

        assert output_path.exists()
        plt.close(chart._fig)

    def test_custom_title(self, sample_df):
        """Uses custom title when provided."""
        chart = create_team_shot_chart(
            sample_df, team="SAC", title="Sacramento Kings - Game 1"
        )
        assert chart.title == "Sacramento Kings - Game 1"
        plt.close(chart._fig)


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests with real sample data."""

    def test_full_workflow_sample_data(self, sample_df, tmp_path):
        """Full workflow with sample data."""
        # Create chart
        chart = ShotChart(sample_df, title="Kings vs Opponents")
        fig, ax = chart.plot()

        # Verify figure
        assert fig is not None
        assert ax is not None

        # Save
        output_path = tmp_path / "integration_test.png"
        chart.save(output_path)
        assert output_path.exists()

        # Close
        chart.close()
        assert chart._fig is None

    def test_multiple_player_charts(self, sample_df, tmp_path):
        """Can create multiple charts for different players."""
        players = sample_df['player_name'].unique()

        for player in players:
            player_shots = filter_shots(sample_df, player_name=player)
            chart = ShotChart(player_shots, title=player)
            chart.plot()

            safe_name = player.replace("'", "").replace(" ", "_")
            output_path = tmp_path / f"{safe_name}_chart.png"
            chart.save(output_path)

            assert output_path.exists()
            chart.close()

    def test_filtered_shot_chart(self, sample_df, tmp_path):
        """Chart with filtered data (3PT only)."""
        three_pt_shots = filter_shots(sample_df, shot_type="3PT")
        chart = ShotChart(three_pt_shots, title="Kings 3-Pointers")
        chart.plot()

        output_path = tmp_path / "three_pointers.png"
        chart.save(output_path)

        assert output_path.exists()
        chart.close()

    def test_fox_shot_chart_with_real_data(self, fox_shots, tmp_path):
        """Create Fox shot chart with real sample data."""
        chart = ShotChart(fox_shots, title="De'Aaron Fox")
        fig, ax = chart.plot()

        # Verify title includes stats
        title = ax.get_title()
        assert "De'Aaron Fox" in title
        assert "FG:" in title

        output_path = tmp_path / "fox_shots.png"
        chart.save(output_path)

        assert output_path.exists()
        chart.close()
