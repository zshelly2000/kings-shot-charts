"""
Utilities module for Kings Shot Chart Generator.

This module provides configuration constants and helper functions.
"""

from src.utils.config import (
    # Court dimensions
    COURT_WIDTH,
    COURT_LENGTH,
    HALF_COURT_LENGTH,
    THREE_POINT_RADIUS,
    THREE_POINT_CORNER_DISTANCE,
    PAINT_WIDTH,
    PAINT_LENGTH,
    FREE_THROW_CIRCLE_RADIUS,
    RESTRICTED_AREA_RADIUS,
    # Colors
    COURT_LINE_COLOR,
    COURT_BG_COLOR,
    MADE_SHOT_COLOR,
    MISSED_SHOT_COLOR,
    KINGS_PURPLE,
    KINGS_GRAY,
    # Settings
    DEFAULT_FIGURE_SIZE,
    DEFAULT_SEASON,
    KINGS_TEAM_ID,
    NBA_API_SCALE,
)

__all__ = [
    "COURT_WIDTH",
    "COURT_LENGTH",
    "HALF_COURT_LENGTH",
    "THREE_POINT_RADIUS",
    "THREE_POINT_CORNER_DISTANCE",
    "PAINT_WIDTH",
    "PAINT_LENGTH",
    "FREE_THROW_CIRCLE_RADIUS",
    "RESTRICTED_AREA_RADIUS",
    "COURT_LINE_COLOR",
    "COURT_BG_COLOR",
    "MADE_SHOT_COLOR",
    "MISSED_SHOT_COLOR",
    "KINGS_PURPLE",
    "KINGS_GRAY",
    "DEFAULT_FIGURE_SIZE",
    "DEFAULT_SEASON",
    "KINGS_TEAM_ID",
    "NBA_API_SCALE",
]
