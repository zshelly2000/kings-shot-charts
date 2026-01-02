# Kings Shot Chart Generator

## Project Overview
A data visualization tool to create interactive shot charts for Sacramento Kings games, showing where shots were taken and their outcomes.

## Project Goals
- Generate visual shot charts from game data
- Show shot location, type (2PT/3PT), and outcome (made/missed)
- Provide filtering by player, quarter, game, etc.
- Create shareable/exportable charts

## Tech Stack
- **Language**: Python 3.11+
- **Data**: NBA API / Manual CSV input
- **Visualization**: Matplotlib, Plotly, or similar
- **Web Interface** (optional): Streamlit or Flask

## Current Status
🚧 **Phase**: Environment Setup & Planning
- [x] Environment setup complete
- [x] Project structure created
- [ ] Requirements defined
- [ ] Data source identified
- [ ] Initial prototype

## Development Principles

### Code Style
- Follow PEP 8 for Python
- Use type hints where appropriate
- Write docstrings for functions/classes
- Keep functions small and focused

### Testing
- Write tests as we build features
- Test with real Kings game data
- Validate visualizations manually

### Documentation
- Keep this CLAUDE.md updated as we progress
- Document data sources and API usage
- Add comments for complex logic

## File Structure
```
kings-shot-charts/
├── .claude/              # Claude Code config
│   └── commands/         # Custom commands
├── docs/                 # Documentation
│   ├── ai/              # AI interaction logs
│   └── specs/           # Project specifications
├── src/                 # Source code (to be created)
│   ├── data/           # Data fetching/processing
│   ├── visualization/  # Chart generation
│   └── utils/          # Helper functions
├── tests/               # Test files
├── data/                # Sample data files
├── output/              # Generated charts
├── .gitignore
├── CLAUDE.md            # This file
├── README.md
└── requirements.txt     # Python dependencies
```

## Data Sources
- NBA Stats API (nba_api Python package)
- Manual CSV upload option
- Focus on Sacramento Kings games (2023-24 season)

## Key Features (Planned)
1. **Data Collection**: Fetch shot data from NBA API
2. **Court Visualization**: Draw NBA court with accurate dimensions
3. **Shot Plotting**: Plot shots with color coding (made/missed)
4. **Filtering**: By player, quarter, shot type, date range
5. **Export**: Save as PNG/PDF/SVG
6. **Interactive** (stretch): Web interface with Streamlit

## Commands for Claude Code

### Custom Commands (in .claude/commands/)
- `spec`: Generate detailed feature specification
- `implement`: Implement a feature from spec
- `test`: Generate tests for a module
- `refactor`: Improve code quality

### Standard Workflow
1. **Spec first**: Always write spec in docs/specs/ before coding
2. **Test-driven**: Write tests alongside features
3. **Iterate**: Build in small, testable increments
4. **Document**: Update CLAUDE.md and add inline comments

## Communication Guidelines
- Ask clarifying questions before big decisions
- Suggest multiple approaches when there are trade-offs
- Explain technical choices clearly
- Show progress with checkpoints

## Notes for AI
- User is learning Python and data visualization
- Explain concepts when introducing new libraries
- Provide examples and documentation links
- Encourage best practices but keep it practical

---
**Last Updated**: January 2, 2026
**Current Phase**: Setup
**Next Steps**: Define detailed requirements and data structure
