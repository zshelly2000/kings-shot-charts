# Kings Shot Chart Generator - Project Specification

## Executive Summary
A Python-based tool that generates visual shot charts for Sacramento Kings basketball games, showing shot locations, outcomes, and player performance through interactive visualizations.

---

## 1. Project Goals

### Primary Goals
- Create accurate NBA court visualizations with proper dimensions
- Plot shot attempts with location data (x, y coordinates)
- Color-code shots by outcome (made/missed)
- Filter data by player, game, quarter, shot type
- Export charts as image files (PNG, PDF)

### Stretch Goals
- Interactive web interface (Streamlit)
- Shot heatmaps showing hot/cold zones
- Comparison charts (player vs player, game vs game)
- Animated shot sequences
- Real-time game data integration

---

## 2. User Stories

### Story 1: Basic Shot Chart
**As a** Kings fan  
**I want** to see a visual chart of where shots were taken in a game  
**So that** I can understand shooting patterns and player tendencies

**Acceptance Criteria:**
- Court is drawn to scale with accurate NBA dimensions
- Shots are plotted at correct locations
- Made shots and missed shots are visually distinct
- Chart includes game/player information

### Story 2: Player Filtering
**As a** fantasy basketball player  
**I want** to filter shots by specific players  
**So that** I can analyze individual player performance

**Acceptance Criteria:**
- Can select one or multiple players
- Chart updates to show only selected players' shots
- Player names are displayed in legend

### Story 3: Export Charts
**As a** content creator  
**I want** to export shot charts as high-quality images  
**So that** I can share them on social media or in articles

**Acceptance Criteria:**
- Can save as PNG, PDF, or SVG
- Image quality is suitable for social media (1080x1080 minimum)
- File naming includes game/player/date information

---

## 3. Technical Requirements

### 3.1 Functional Requirements
- **FR1**: Fetch shot data from NBA Stats API
- **FR2**: Parse and validate shot coordinate data
- **FR3**: Draw NBA regulation court (94' x 50')
- **FR4**: Plot shots with accurate positioning
- **FR5**: Apply color schemes (made = green, missed = red, or customizable)
- **FR6**: Filter by: player, game, date range, quarter, shot type (2PT/3PT)
- **FR7**: Display shot statistics (FG%, 3P%, etc.)
- **FR8**: Export visualization to file
- **FR9**: Handle missing or invalid data gracefully

### 3.2 Non-Functional Requirements
- **NFR1**: Performance - Generate chart in < 5 seconds
- **NFR2**: Accuracy - Court dimensions within 1% of NBA specs
- **NFR3**: Usability - Clear error messages for invalid inputs
- **NFR4**: Reliability - Handle API rate limits and timeouts
- **NFR5**: Maintainability - Modular code structure
- **NFR6**: Scalability - Handle full season data (82 games)

---

## 4. Data Structure

### 4.1 Shot Data Schema
```python
Shot = {
    'game_id': str,           # e.g., '0022300123'
    'player_id': int,         # NBA player ID
    'player_name': str,       # e.g., 'De'Aaron Fox'
    'team': str,              # 'SAC'
    'period': int,            # 1-4 (5+ for OT)
    'minutes_remaining': int,
    'seconds_remaining': int,
    'shot_made': bool,        # True if made
    'shot_type': str,         # '2PT Field Goal' or '3PT Field Goal'
    'shot_distance': float,   # Distance in feet
    'loc_x': float,           # X coordinate (in feet, centered)
    'loc_y': float,           # Y coordinate (in feet)
    'shot_zone': str,         # e.g., 'Left Corner 3'
    'action_type': str        # e.g., 'Jump Shot', 'Layup'
}
```

### 4.2 Game Data Schema
```python
Game = {
    'game_id': str,
    'game_date': date,
    'home_team': str,
    'away_team': str,
    'home_score': int,
    'away_score': int,
    'season': str             # e.g., '2023-24'
}
```

---

## 5. System Architecture

### 5.1 Module Structure
```
src/
├── data/
│   ├── __init__.py
│   ├── nba_api_client.py    # Fetch data from NBA API
│   ├── data_loader.py       # Load from CSV/JSON
│   └── data_processor.py    # Clean and transform data
├── visualization/
│   ├── __init__.py
│   ├── court.py             # Draw NBA court
│   ├── shot_chart.py        # Main chart generation
│   └── styles.py            # Color schemes and styling
├── utils/
│   ├── __init__.py
│   ├── config.py            # Configuration constants
│   └── helpers.py           # Utility functions
└── main.py                  # CLI entry point
```

### 5.2 Key Classes/Functions

#### CourtDrawer
```python
class CourtDrawer:
    """Handles drawing NBA court with accurate dimensions"""
    
    def __init__(self, fig_size=(12, 11)):
        """Initialize with figure size"""
        
    def draw_court(self, ax, color='black', lw=2):
        """Draw court elements on matplotlib axis"""
        
    def get_court_dimensions(self):
        """Return dict of court measurements"""
```

#### ShotChart
```python
class ShotChart:
    """Main class for generating shot charts"""
    
    def __init__(self, shots_df, game_info=None):
        """Initialize with shot data"""
        
    def plot(self, player=None, made_color='green', 
             missed_color='red', **kwargs):
        """Generate shot chart visualization"""
        
    def save(self, filename, dpi=300):
        """Export chart to file"""
        
    def add_statistics(self, position='top'):
        """Add shooting statistics to chart"""
```

#### NBADataFetcher
```python
class NBADataFetcher:
    """Fetch shot data from NBA Stats API"""
    
    def get_game_shots(self, game_id):
        """Fetch all shots from a game"""
        
    def get_player_shots(self, player_id, season='2023-24'):
        """Fetch all shots for a player in a season"""
        
    def get_team_schedule(self, team_id, season='2023-24'):
        """Fetch team's game schedule"""
```

---

## 6. UI/Output Specification

### 6.1 Command Line Interface (Phase 1)
```bash
# Generate shot chart for a specific game
python main.py --game-id 0022300123 --team SAC --output game_123.png

# Generate shot chart for specific player
python main.py --player "De'Aaron Fox" --season 2023-24 --output fox_season.png

# Filter by date range
python main.py --team SAC --start-date 2024-01-01 --end-date 2024-01-31
```

### 6.2 Web Interface (Phase 2 - Stretch)
- Dropdown to select team/player
- Date range picker
- Checkboxes for filters (quarter, shot type)
- Preview of chart
- Download button for export

### 6.3 Chart Visual Elements
1. **Court Background**: Gray or white
2. **Court Lines**: Black, 2pt line width
3. **Shot Markers**: Circles, size 100
   - Made: Green (or customizable)
   - Missed: Red with X marker
4. **Title**: "{Player Name} - {Game Date}" or "{Team} Shot Chart"
5. **Legend**: Shows made/missed with counts
6. **Statistics Box**: 
   - FG: X/Y (Z%)
   - 3PT: X/Y (Z%)
   - 2PT: X/Y (Z%)

---

## 7. Edge Cases & Error Handling

### Data Issues
- **Empty dataset**: Display message "No shots found for criteria"
- **Invalid game_id**: "Game not found. Check game ID."
- **API timeout**: Retry 3 times with exponential backoff
- **Missing coordinates**: Skip shot, log warning
- **Invalid player name**: Suggest similar names

### Visualization Issues
- **Too many shots** (>500): Reduce marker size for clarity
- **Single shot**: Still draw full court, show stats
- **All made or all missed**: Adjust legend accordingly

### Export Issues
- **Invalid filename**: Sanitize, remove special characters
- **File exists**: Prompt to overwrite or append timestamp
- **Permission denied**: Clear error message with path

---

## 8. Testing Strategy

### Unit Tests
- `test_court_dimensions()`: Verify court measurements
- `test_shot_coordinates()`: Validate coordinate transformations
- `test_data_parsing()`: Check data cleaning logic
- `test_filtering()`: Verify filter functions

### Integration Tests
- `test_full_chart_generation()`: End-to-end chart creation
- `test_api_integration()`: Fetch real data and generate chart
- `test_export_formats()`: Verify PNG, PDF outputs

### Manual Testing
- Visual inspection of court proportions
- Compare generated chart with official NBA shot charts
- Test with Kings games from 2023-24 season
- Verify player names and statistics match box scores

---

## 9. Implementation Plan

### Phase 1: Core Foundation (Week 1)
- [ ] Set up project structure
- [ ] Install dependencies
- [ ] Create court drawing module
- [ ] Implement basic shot plotting
- [ ] Test with sample data

### Phase 2: Data Integration (Week 2)
- [ ] Set up NBA API connection
- [ ] Implement data fetching
- [ ] Add data processing/cleaning
- [ ] Create data validation

### Phase 3: Features & Filters (Week 3)
- [ ] Implement filtering (player, date, shot type)
- [ ] Add statistics calculations
- [ ] Improve visual styling
- [ ] Add export functionality

### Phase 4: Polish & Testing (Week 4)
- [ ] Write comprehensive tests
- [ ] Add error handling
- [ ] Create documentation
- [ ] Optimize performance

### Phase 5: Stretch Goals (Optional)
- [ ] Build Streamlit web interface
- [ ] Add shot heatmaps
- [ ] Implement shot animations
- [ ] Add comparison features

---

## 10. Dependencies & Tools

### Core Libraries
- `matplotlib` - Visualization
- `pandas` - Data manipulation
- `nba_api` - NBA data access
- `numpy` - Numerical operations

### Optional Libraries
- `seaborn` - Enhanced styling
- `plotly` - Interactive charts (stretch)
- `streamlit` - Web interface (stretch)

### Development Tools
- `pytest` - Testing
- `black` - Code formatting
- `mypy` - Type checking

---

## 11. Success Metrics

### Minimum Viable Product (MVP)
✅ Generate accurate shot chart for any Kings game  
✅ Filter by player  
✅ Export as PNG with good quality  
✅ Complete in < 5 seconds  

### Full Success
✅ All MVP features  
✅ Multiple filter options  
✅ Professional-looking charts  
✅ Well-tested and documented  
✅ Easy to use CLI  

### Excellence
✅ Full success criteria  
✅ Web interface  
✅ Advanced visualizations (heatmaps)  
✅ Comparison features  

---

## 12. Open Questions

1. **Data Source**: Should we cache API responses to avoid rate limits?
2. **Coordinate System**: NBA API uses different coordinate systems - which to standardize on?
3. **Team Focus**: Start with Kings only or support all NBA teams?
4. **Historical Data**: How far back should we support (2023-24 season? Last 5 years?)
5. **Output Format**: Is PNG sufficient or do we need vector formats (SVG)?

---

## 13. Resources & References

- [NBA Stats API Documentation](https://github.com/swar/nba_api)
- [NBA Court Dimensions](https://www.sportsknowhow.com/basketball/dimensions/nba-basketball-court-dimensions.html)
- [Matplotlib Shot Chart Tutorial](https://github.com/bradleyfay/py-Goldsberry)
- [Official NBA Court Specs](https://official.nba.com/rulebook/)

---

**Document Version**: 1.0  
**Last Updated**: January 2, 2026  
**Status**: Approved for Development  
**Next Review**: After Phase 1 completion
