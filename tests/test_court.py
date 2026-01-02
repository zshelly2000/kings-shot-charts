"""
Unit tests for the court drawing module.

Tests verify that:
1. Court dimensions match NBA specifications
2. CourtDrawer creates valid matplotlib objects
3. All court elements are drawn correctly
"""

import pytest
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from src.visualization.court import CourtDrawer, draw_court
from src.utils.config import (
    COURT_WIDTH,
    HALF_COURT_LENGTH,
    THREE_POINT_RADIUS,
    THREE_POINT_CORNER_DISTANCE,
    PAINT_WIDTH,
    PAINT_LENGTH,
    FREE_THROW_CIRCLE_RADIUS,
    RESTRICTED_AREA_RADIUS,
    CENTER_CIRCLE_RADIUS,
    DEFAULT_FIGURE_SIZE,
)


class TestCourtDimensions:
    """Test that court dimensions match NBA specifications."""

    def test_court_width(self):
        """NBA court is 50 feet wide."""
        assert COURT_WIDTH == 50.0

    def test_half_court_length(self):
        """Half court is 47 feet long."""
        assert HALF_COURT_LENGTH == 47.0

    def test_three_point_radius(self):
        """Three-point line is 23.75 feet from basket (arc)."""
        assert THREE_POINT_RADIUS == 23.75

    def test_three_point_corner(self):
        """Corner three is 22 feet from basket."""
        assert THREE_POINT_CORNER_DISTANCE == 22.0

    def test_paint_dimensions(self):
        """Paint is 16 feet wide and 19 feet long."""
        assert PAINT_WIDTH == 16.0
        assert PAINT_LENGTH == 19.0

    def test_free_throw_circle_radius(self):
        """Free throw circle has 6 foot radius."""
        assert FREE_THROW_CIRCLE_RADIUS == 6.0

    def test_restricted_area_radius(self):
        """Restricted area has 4 foot radius."""
        assert RESTRICTED_AREA_RADIUS == 4.0

    def test_center_circle_radius(self):
        """Center circle has 6 foot radius."""
        assert CENTER_CIRCLE_RADIUS == 6.0


class TestCourtDrawer:
    """Test the CourtDrawer class."""

    def test_init_default_values(self):
        """CourtDrawer initializes with correct defaults."""
        court = CourtDrawer()
        assert court.fig_size == DEFAULT_FIGURE_SIZE
        assert court.line_color == "#000000"
        assert court.line_width == 2.0

    def test_init_custom_values(self):
        """CourtDrawer accepts custom initialization values."""
        court = CourtDrawer(
            fig_size=(10, 9),
            line_color="blue",
            line_width=3.0,
            court_color="white",
        )
        assert court.fig_size == (10, 9)
        assert court.line_color == "blue"
        assert court.line_width == 3.0
        assert court.court_color == "white"

    def test_get_court_dimensions(self):
        """get_court_dimensions returns correct NBA measurements."""
        court = CourtDrawer()
        dims = court.get_court_dimensions()

        assert dims["court_width"] == 50.0
        assert dims["half_court_length"] == 47.0
        assert dims["three_point_radius"] == 23.75
        assert dims["three_point_corner"] == 22.0
        assert dims["paint_width"] == 16.0
        assert dims["paint_length"] == 19.0

    def test_draw_court_returns_axes(self):
        """draw_court returns a matplotlib Axes object."""
        court = CourtDrawer()
        fig, ax = plt.subplots()
        result = court.draw_court(ax)

        assert isinstance(result, Axes)
        plt.close(fig)

    def test_draw_court_creates_figure_when_no_ax(self):
        """draw_court creates figure when no axes provided."""
        court = CourtDrawer()
        ax = court.draw_court()

        assert isinstance(ax, Axes)
        plt.close("all")

    def test_draw_court_with_custom_colors(self):
        """draw_court accepts color overrides."""
        court = CourtDrawer()
        fig, ax = plt.subplots()

        # Should not raise any errors
        result = court.draw_court(ax, color="navy", lw=3)
        assert isinstance(result, Axes)
        plt.close(fig)

    def test_draw_court_with_outer_lines(self):
        """draw_court can draw boundary lines."""
        court = CourtDrawer()
        fig, ax = plt.subplots()

        # Should not raise any errors
        result = court.draw_court(ax, outer_lines=True)
        assert isinstance(result, Axes)
        plt.close(fig)

    def test_create_figure_returns_tuple(self):
        """create_figure returns (Figure, Axes) tuple."""
        court = CourtDrawer()
        result = court.create_figure()

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Figure)
        assert isinstance(result[1], Axes)
        plt.close(result[0])

    def test_court_has_patches(self):
        """Court drawing adds patches to axes."""
        court = CourtDrawer()
        fig, ax = plt.subplots()
        court.draw_court(ax)

        # Court should have multiple patches (basket, paint, arcs, etc.)
        assert len(ax.patches) > 0
        plt.close(fig)

    def test_court_has_correct_aspect_ratio(self):
        """Court maintains equal aspect ratio."""
        court = CourtDrawer()
        fig, ax = plt.subplots()
        court.draw_court(ax)

        # Aspect should be 'equal'
        assert ax.get_aspect() == 1.0  # Equal aspect ratio
        plt.close(fig)


class TestDrawCourtFunction:
    """Test the convenience draw_court function."""

    def test_draw_court_function_returns_axes(self):
        """draw_court function returns Axes."""
        fig, ax = plt.subplots()
        result = draw_court(ax)

        assert isinstance(result, Axes)
        plt.close(fig)

    def test_draw_court_function_creates_figure(self):
        """draw_court function creates figure when needed."""
        ax = draw_court()
        assert isinstance(ax, Axes)
        plt.close("all")

    def test_draw_court_function_accepts_parameters(self):
        """draw_court function accepts color and line width."""
        fig, ax = plt.subplots()

        # Should not raise any errors
        result = draw_court(ax, color="red", lw=4)
        assert isinstance(result, Axes)
        plt.close(fig)


class TestCourtVisualization:
    """Integration tests for court visualization."""

    def test_full_court_render(self):
        """Full court renders without errors."""
        court = CourtDrawer()
        fig, ax = court.create_figure()

        # Verify axis limits are set (in NBA API units)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # X should be roughly -260 to 260 (court width + margins)
        assert xlim[0] < -200
        assert xlim[1] > 200

        # Y should be roughly -50 to 440 (baseline to half court + margins)
        assert ylim[0] < 0
        assert ylim[1] > 400

        plt.close(fig)

    def test_court_can_be_saved(self, tmp_path):
        """Court can be saved to file."""
        court = CourtDrawer()
        fig, ax = court.create_figure()

        output_file = tmp_path / "test_court.png"
        fig.savefig(output_file, dpi=100)

        assert output_file.exists()
        assert output_file.stat().st_size > 0
        plt.close(fig)
