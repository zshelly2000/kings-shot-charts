# Development Guide - Kings Shot Chart Generator

## Getting Started

This guide will help you set up your development environment and start building the Kings Shot Chart Generator.

## Environment Setup Checklist

- [x] Python 3.11+ installed
- [x] Git installed and configured
- [x] VS Code with extensions installed
- [x] Project structure created
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] First test passed

## Step-by-Step Setup

### 1. Create Virtual Environment

A virtual environment keeps your project dependencies isolated from other Python projects.

```bash
# Navigate to your project folder
cd ~/projects/kings-shot-charts

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 2. Install Dependencies

```bash
# Make sure venv is activated (you should see (venv) in your prompt)
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Verify Setup

```bash
# Test Python can find the modules
python -c "import matplotlib; import pandas; import nba_api; print('All imports successful!')"
```

## Development Workflow

### Daily Workflow

1. **Activate virtual environment**
   ```bash
   # Always activate before working
   venv\Scripts\activate  # Windows
   ```

2. **Pull latest changes** (if using Git)
   ```bash
   git pull
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/court-drawing
   ```

4. **Make changes and test frequently**
   ```bash
   # Run tests
   pytest tests/
   
   # Run specific test
   pytest tests/test_court.py
   ```

5. **Commit your work**
   ```bash
   git add .
   git commit -m "Add court drawing functionality"
   ```

6. **Push to GitHub**
   ```bash
   git push origin feature/court-drawing
   ```

### Code Quality Checks

Before committing, run these:

```bash
# Format code
black src/ tests/

# Check for issues
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Development Phases

### Phase 1: Core Foundation (Current)

**Goal**: Draw an accurate NBA court and plot basic shots

**Tasks**:
1. Create `src/visualization/court.py` - Draw NBA court
2. Create `src/visualization/shot_chart.py` - Plot shots
3. Create sample data file with test shots
4. Write tests for court dimensions

**Success Criteria**:
- ✅ Court renders with correct dimensions
- ✅ Can plot at least one shot
- ✅ Tests pass

### Phase 2: Data Integration

**Goal**: Fetch real game data from NBA API

**Tasks**:
1. Create `src/data/nba_api_client.py`
2. Implement game data fetching
3. Add data validation
4. Create data caching mechanism

**Success Criteria**:
- ✅ Can fetch real Kings game data
- ✅ Data is properly formatted
- ✅ API errors handled gracefully

### Phase 3: Features & Filters

**Goal**: Add filtering and customization

**Tasks**:
1. Implement player filtering
2. Add date range filtering
3. Create statistics calculations
4. Add customizable colors/styles

### Phase 4: Polish & Export

**Goal**: Production-ready charts

**Tasks**:
1. Export functionality (PNG, PDF, SVG)
2. Professional styling
3. Comprehensive error handling
4. User documentation

## Useful Commands

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_court.py

# Run tests matching a pattern
pytest -k "test_court"
```

### Python REPL (Interactive Testing)

```bash
# Start Python interpreter
python

# Quick test imports and functions
>>> from src.visualization.court import CourtDrawer
>>> court = CourtDrawer()
>>> print(court.get_court_dimensions())
```

### Package Management

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Show installed packages
pip list

# Show package info
pip show matplotlib
```

## Debugging Tips

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`
**Solution**: Make sure you're in the project root and venv is activated

**Issue**: `ImportError: cannot import name X`
**Solution**: Check your `__init__.py` files exist in each package folder

**Issue**: API rate limit errors
**Solution**: Implement caching and add delays between requests

### VS Code Debugging

1. Click on the "Run and Debug" icon (play button with bug)
2. Click "create a launch.json file"
3. Select "Python File"
4. Set breakpoints by clicking left of line numbers
5. Press F5 to start debugging

## Learning Resources

### Python & Data Science
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NBA API Documentation](https://github.com/swar/nba_api)

### Basketball Analytics
- [Basketball Reference](https://www.basketball-reference.com/)
- [NBA Stats](https://www.nba.com/stats)
- [Shot Chart Examples](https://savvytime.com/converter/pst-to-est)

### Best Practices
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Git Best Practices](https://www.git-scm.com/book/en/v2)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)

## Getting Help

1. **Check the specs** - See `docs/specs/` for detailed documentation
2. **Read error messages** - They usually tell you what's wrong
3. **Use print statements** - Simple but effective debugging
4. **Check the CLAUDE.md** - Project context and guidelines
5. **Ask questions** - Open an issue or ask for help

## Next Steps

Now that your environment is set up:

1. ✅ Verify all imports work
2. Create your first module (`court.py`)
3. Write your first test
4. Draw your first court!

Let's build something awesome! 🏀🔥

---
**Last Updated**: January 2, 2026
