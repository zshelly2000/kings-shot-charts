"""
Configuration constants for Kings Shot Chart Generator.

This module contains NBA court dimensions and default settings.
All measurements are in feet unless otherwise noted.
"""

# =============================================================================
# NBA COURT DIMENSIONS (in feet)
# Official NBA court specifications
# =============================================================================

# Court size
COURT_LENGTH = 94.0  # Full court length
COURT_WIDTH = 50.0   # Court width
HALF_COURT_LENGTH = 47.0  # Half court length

# Basket and backboard
BASKET_DIAMETER = 1.5  # 18 inches
BACKBOARD_WIDTH = 6.0
BACKBOARD_OFFSET = 4.0  # Distance from baseline to front of rim

# Three-point line
THREE_POINT_RADIUS = 23.75  # Arc radius from center of basket
THREE_POINT_CORNER_DISTANCE = 22.0  # Corner three distance
THREE_POINT_SIDE_LENGTH = 14.0  # Length of straight section along sideline

# Paint / Key area
PAINT_WIDTH = 16.0  # Width of the paint
PAINT_LENGTH = 19.0  # Length from baseline to free throw line

# Free throw
FREE_THROW_LINE_DISTANCE = 15.0  # From front of backboard (19 from baseline)
FREE_THROW_CIRCLE_RADIUS = 6.0

# Restricted area (under basket)
RESTRICTED_AREA_RADIUS = 4.0

# Center court
CENTER_CIRCLE_RADIUS = 6.0
CENTER_CIRCLE_OUTER_RADIUS = 2.0  # Inner circle (just for half court line)

# =============================================================================
# NBA API COORDINATE SYSTEM
# The NBA API uses a coordinate system in tenths of feet
# =============================================================================

# NBA API scale factor (coordinates are in tenths of feet)
NBA_API_SCALE = 10.0

# Court bounds in NBA API coordinates
# X: -250 to 250 (sideline to sideline, centered)
# Y: -47.5 to 422.5 (baseline to opposite baseline, offensive basket at Y=0)
NBA_API_X_MIN = -250
NBA_API_X_MAX = 250
NBA_API_Y_MIN = -52.5  # Slightly behind baseline
NBA_API_Y_MAX = 417.5  # Slightly past half court for viz

# =============================================================================
# VISUALIZATION DEFAULTS
# =============================================================================

# Figure size for shot charts (width, height in inches)
DEFAULT_FIGURE_SIZE = (12, 11)

# Court colors
COURT_LINE_COLOR = "#000000"  # Black lines
COURT_BG_COLOR = "#F5F5F5"    # Light gray background

# Shot marker colors (Kings purple and gray theme option available)
MADE_SHOT_COLOR = "#5A2D82"   # Kings purple for made shots
MISSED_SHOT_COLOR = "#8B8B8B"  # Gray for missed shots

# Alternative color scheme (traditional)
MADE_SHOT_COLOR_ALT = "#228B22"   # Green
MISSED_SHOT_COLOR_ALT = "#DC143C"  # Crimson red

# Marker settings
SHOT_MARKER_SIZE = 80
SHOT_MARKER_ALPHA = 0.7

# Line widths
COURT_LINE_WIDTH = 2.0
SHOT_MARKER_EDGE_WIDTH = 1.0

# =============================================================================
# TEAM INFORMATION
# =============================================================================

# Sacramento Kings
KINGS_TEAM_ID = 1610612758
KINGS_ABBREVIATION = "SAC"
KINGS_FULL_NAME = "Sacramento Kings"

# Kings colors
KINGS_PURPLE = "#5A2D82"
KINGS_GRAY = "#63727A"
KINGS_BLACK = "#000000"
KINGS_WHITE = "#FFFFFF"

# =============================================================================
# API SETTINGS
# =============================================================================

# Rate limiting
API_TIMEOUT = 30  # seconds
API_RETRY_COUNT = 3
API_RETRY_DELAY = 1.0  # seconds between retries

# Default season
DEFAULT_SEASON = "2024-25"
