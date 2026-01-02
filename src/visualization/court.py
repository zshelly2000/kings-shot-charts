"""
NBA Court Drawing Module.

This module provides the CourtDrawer class for creating accurate
NBA basketball court visualizations using matplotlib.

The court is drawn using NBA official dimensions and is compatible
with the NBA API coordinate system for shot plotting.

Example:
    >>> from src.visualization.court import CourtDrawer
    >>> import matplotlib.pyplot as plt
    >>>
    >>> fig, ax = plt.subplots(figsize=(12, 11))
    >>> court = CourtDrawer()
    >>> court.draw_court(ax)
    >>> plt.show()
"""

from typing import Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Wedge
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np

from src.utils.config import (
    COURT_WIDTH,
    HALF_COURT_LENGTH,
    BASKET_DIAMETER,
    BACKBOARD_OFFSET,
    THREE_POINT_RADIUS,
    THREE_POINT_CORNER_DISTANCE,
    THREE_POINT_SIDE_LENGTH,
    PAINT_WIDTH,
    PAINT_LENGTH,
    FREE_THROW_CIRCLE_RADIUS,
    RESTRICTED_AREA_RADIUS,
    CENTER_CIRCLE_RADIUS,
    DEFAULT_FIGURE_SIZE,
    COURT_LINE_COLOR,
    COURT_BG_COLOR,
    COURT_LINE_WIDTH,
    NBA_API_SCALE,
)


class CourtDrawer:
    """
    Handles drawing an NBA basketball court with accurate dimensions.

    The court is drawn in NBA API coordinate space where:
    - X axis: -250 to 250 (sideline to sideline, in tenths of feet)
    - Y axis: -52.5 to ~420 (behind baseline to past half court)
    - Origin (0, 0) is at the center of the basket

    This coordinate system matches the NBA Stats API shot chart data,
    allowing shots to be plotted directly without transformation.

    Attributes:
        fig_size: Tuple of (width, height) in inches for the figure.
        line_color: Color of court lines.
        line_width: Width of court lines.
        court_color: Background color of the court.
    """

    def __init__(
        self,
        fig_size: Tuple[float, float] = DEFAULT_FIGURE_SIZE,
        line_color: str = COURT_LINE_COLOR,
        line_width: float = COURT_LINE_WIDTH,
        court_color: str = COURT_BG_COLOR,
    ) -> None:
        """
        Initialize CourtDrawer with display settings.

        Args:
            fig_size: Figure dimensions as (width, height) in inches.
            line_color: Color for court lines (default: black).
            line_width: Width of court lines (default: 2.0).
            court_color: Background color of court (default: light gray).
        """
        self.fig_size = fig_size
        self.line_color = line_color
        self.line_width = line_width
        self.court_color = court_color

    def draw_court(
        self,
        ax: Optional[Axes] = None,
        color: Optional[str] = None,
        lw: Optional[float] = None,
        outer_lines: bool = False,
    ) -> Axes:
        """
        Draw an NBA half-court on a matplotlib axes.

        The court is drawn with the basket at the bottom, oriented
        so shots from the NBA API can be plotted directly.

        Args:
            ax: Matplotlib axes to draw on. If None, creates new figure.
            color: Override line color for this drawing.
            lw: Override line width for this drawing.
            outer_lines: If True, draw the outer boundary lines.

        Returns:
            The matplotlib Axes object with the court drawn.

        Example:
            >>> fig, ax = plt.subplots()
            >>> court = CourtDrawer()
            >>> ax = court.draw_court(ax)
        """
        # Use instance defaults if not overridden
        color = color or self.line_color
        lw = lw or self.line_width

        # Create figure and axes if not provided
        if ax is None:
            fig, ax = plt.subplots(figsize=self.fig_size)

        # Set background color
        ax.set_facecolor(self.court_color)

        # All coordinates are in NBA API units (tenths of feet)
        # Basket is at origin (0, 0)

        # --- Draw court elements from bottom to top ---

        # 1. Basket (hoop)
        basket_radius = (BASKET_DIAMETER / 2) * NBA_API_SCALE
        basket = Circle(
            (0, 0),
            radius=basket_radius,
            linewidth=lw,
            color=color,
            fill=False,
        )
        ax.add_patch(basket)

        # 2. Backboard
        backboard_y = -BACKBOARD_OFFSET * NBA_API_SCALE + 7.5  # Slight offset for visual
        backboard_width = 60  # 6 feet in tenths
        backboard = Rectangle(
            (-backboard_width / 2, backboard_y),
            backboard_width,
            -1,  # Thin line
            linewidth=lw,
            color=color,
            fill=True,
        )
        ax.add_patch(backboard)

        # 3. Restricted area arc (4 ft radius)
        restricted_radius = RESTRICTED_AREA_RADIUS * NBA_API_SCALE
        restricted = Arc(
            (0, 0),
            restricted_radius * 2,
            restricted_radius * 2,
            theta1=0,
            theta2=180,
            linewidth=lw,
            color=color,
        )
        ax.add_patch(restricted)

        # 4. Paint / Key area (16 ft wide, 19 ft long)
        paint_width = PAINT_WIDTH * NBA_API_SCALE
        paint_length = PAINT_LENGTH * NBA_API_SCALE

        # Paint box
        paint = Rectangle(
            (-paint_width / 2, -BACKBOARD_OFFSET * NBA_API_SCALE),
            paint_width,
            paint_length,
            linewidth=lw,
            color=color,
            fill=False,
        )
        ax.add_patch(paint)

        # 5. Free throw circle (6 ft radius)
        ft_radius = FREE_THROW_CIRCLE_RADIUS * NBA_API_SCALE
        ft_line_y = (PAINT_LENGTH - BACKBOARD_OFFSET) * NBA_API_SCALE

        # Top half of free throw circle (solid)
        ft_circle_top = Arc(
            (0, ft_line_y),
            ft_radius * 2,
            ft_radius * 2,
            theta1=0,
            theta2=180,
            linewidth=lw,
            color=color,
        )
        ax.add_patch(ft_circle_top)

        # Bottom half of free throw circle (dashed)
        ft_circle_bottom = Arc(
            (0, ft_line_y),
            ft_radius * 2,
            ft_radius * 2,
            theta1=180,
            theta2=360,
            linewidth=lw,
            color=color,
            linestyle="dashed",
        )
        ax.add_patch(ft_circle_bottom)

        # 6. Three-point line
        # The 3pt line has straight sections along the sidelines
        # and an arc connecting them

        three_pt_radius = THREE_POINT_RADIUS * NBA_API_SCALE
        corner_dist = THREE_POINT_CORNER_DISTANCE * NBA_API_SCALE

        # Calculate where the arc meets the straight line
        # Using pythagorean theorem: x^2 + y^2 = r^2
        # At corner_dist from sideline, find the y where arc starts
        arc_start_y = np.sqrt(three_pt_radius**2 - corner_dist**2)

        # Left corner three (straight line)
        ax.plot(
            [-corner_dist, -corner_dist],
            [-BACKBOARD_OFFSET * NBA_API_SCALE, arc_start_y],
            linewidth=lw,
            color=color,
        )

        # Right corner three (straight line)
        ax.plot(
            [corner_dist, corner_dist],
            [-BACKBOARD_OFFSET * NBA_API_SCALE, arc_start_y],
            linewidth=lw,
            color=color,
        )

        # Three-point arc
        # Calculate the angle where the arc meets the corner line
        arc_angle = np.degrees(np.arcsin(arc_start_y / three_pt_radius))

        three_pt_arc = Arc(
            (0, 0),
            three_pt_radius * 2,
            three_pt_radius * 2,
            theta1=arc_angle,
            theta2=180 - arc_angle,
            linewidth=lw,
            color=color,
        )
        ax.add_patch(three_pt_arc)

        # 7. Center court elements (half court line and circle)
        half_court_y = (HALF_COURT_LENGTH - BACKBOARD_OFFSET) * NBA_API_SCALE

        # Half court line
        court_half_width = (COURT_WIDTH / 2) * NBA_API_SCALE
        ax.plot(
            [-court_half_width, court_half_width],
            [half_court_y, half_court_y],
            linewidth=lw,
            color=color,
        )

        # Center circle (only bottom half visible on half court)
        center_radius = CENTER_CIRCLE_RADIUS * NBA_API_SCALE
        center_circle = Arc(
            (0, half_court_y),
            center_radius * 2,
            center_radius * 2,
            theta1=180,
            theta2=360,
            linewidth=lw,
            color=color,
        )
        ax.add_patch(center_circle)

        # 8. Outer boundary lines (optional)
        if outer_lines:
            # Baseline
            ax.plot(
                [-court_half_width, court_half_width],
                [-BACKBOARD_OFFSET * NBA_API_SCALE, -BACKBOARD_OFFSET * NBA_API_SCALE],
                linewidth=lw,
                color=color,
            )
            # Left sideline
            ax.plot(
                [-court_half_width, -court_half_width],
                [-BACKBOARD_OFFSET * NBA_API_SCALE, half_court_y],
                linewidth=lw,
                color=color,
            )
            # Right sideline
            ax.plot(
                [court_half_width, court_half_width],
                [-BACKBOARD_OFFSET * NBA_API_SCALE, half_court_y],
                linewidth=lw,
                color=color,
            )

        # Set axis properties for proper display
        ax.set_xlim(-court_half_width - 10, court_half_width + 10)
        ax.set_ylim(-BACKBOARD_OFFSET * NBA_API_SCALE - 10, half_court_y + 10)
        ax.set_aspect("equal")
        ax.axis("off")  # Hide axis ticks and labels

        return ax

    def get_court_dimensions(self) -> dict:
        """
        Return a dictionary of NBA court measurements.

        All dimensions are in feet (not NBA API units).

        Returns:
            Dictionary containing court dimension constants.

        Example:
            >>> court = CourtDrawer()
            >>> dims = court.get_court_dimensions()
            >>> print(f"Three-point distance: {dims['three_point_radius']} feet")
        """
        return {
            "court_width": COURT_WIDTH,
            "half_court_length": HALF_COURT_LENGTH,
            "basket_diameter": BASKET_DIAMETER,
            "backboard_offset": BACKBOARD_OFFSET,
            "three_point_radius": THREE_POINT_RADIUS,
            "three_point_corner": THREE_POINT_CORNER_DISTANCE,
            "paint_width": PAINT_WIDTH,
            "paint_length": PAINT_LENGTH,
            "free_throw_circle_radius": FREE_THROW_CIRCLE_RADIUS,
            "restricted_area_radius": RESTRICTED_AREA_RADIUS,
            "center_circle_radius": CENTER_CIRCLE_RADIUS,
        }

    def create_figure(self) -> Tuple[Figure, Axes]:
        """
        Create a new figure and axes with the court drawn.

        Convenience method that creates a figure, draws the court,
        and returns both for further customization.

        Returns:
            Tuple of (Figure, Axes) with court already drawn.

        Example:
            >>> court = CourtDrawer()
            >>> fig, ax = court.create_figure()
            >>> ax.scatter([0], [50], c='red', s=100)  # Plot a shot
            >>> plt.savefig('shot_chart.png')
        """
        fig, ax = plt.subplots(figsize=self.fig_size)
        self.draw_court(ax)
        return fig, ax


def draw_court(
    ax: Optional[Axes] = None,
    color: str = COURT_LINE_COLOR,
    lw: float = COURT_LINE_WIDTH,
) -> Axes:
    """
    Convenience function to draw a court without instantiating CourtDrawer.

    Args:
        ax: Matplotlib axes to draw on. If None, creates new figure.
        color: Line color for court elements.
        lw: Line width for court elements.

    Returns:
        Matplotlib Axes with court drawn.

    Example:
        >>> import matplotlib.pyplot as plt
        >>> from src.visualization.court import draw_court
        >>>
        >>> fig, ax = plt.subplots(figsize=(12, 11))
        >>> draw_court(ax)
        >>> plt.show()
    """
    drawer = CourtDrawer(line_color=color, line_width=lw)
    return drawer.draw_court(ax)
