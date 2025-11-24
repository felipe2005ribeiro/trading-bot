# Contributing to Trading Bot

First off, thank you for considering contributing to this project! 🎉

## Code of Conduct

This project and everyone participating in it is governed by common sense and mutual respect. Be kind, be professional.

## How Can I Contribute?

### Reporting Bugs

**Before Submitting:**
- Check existing issues to avoid duplicates
- Collect relevant logs from `logs/` directory
- Note your environment (OS, Python version, etc.)

**Submit via GitHub Issues:**
- Use clear, descriptive title
- Describe steps to reproduce
- Include expected vs actual behavior
- Attach logs if applicable

### Suggesting Enhancements

**Feature Requests:**
- Explain the problem it solves
- Describe proposed solution
- Consider alternative approaches
- Think about implementation complexity

### Pull Requests

**Process:**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Commit with clear messages
7. Push to your fork
8. Open Pull Request

**PR Guidelines:**
- One feature/fix per PR
- Clear description of changes
- Reference related issues
- Update README if needed
- Follow existing code style

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (if available)
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings
- Keep functions focused and small

**Example:**
```python
def calculate_position_size(capital: float, risk_percent: float) -> float:
    """
    Calculate position size based on capital and risk.
    
    Args:
        capital: Total available capital
        risk_percent: Percentage of capital to risk
        
    Returns:
        Position size in base currency
    """
    return capital * (risk_percent / 100)
```

### Code Organization

- Modular design
- Separation of concerns
- DRY (Don't Repeat Yourself)
- Clear naming conventions

### Testing

- Add tests for new features
- Ensure existing tests pass
- Test edge cases
- Mock external dependencies

## Areas for Contribution

### High Priority

- [ ] Additional trading strategies
- [ ] More comprehensive testing
- [ ] Performance optimizations
- [ ] Documentation improvements
- [ ] Bug fixes

### Medium Priority

- [ ] Additional exchanges (Bybit, Kucoin)
- [ ] Advanced analytics
- [ ] UI/Dashboard improvements
- [ ] Mobile notifications

### Low Priority

- [ ] Machine learning strategies
- [ ] Social trading features
- [ ] Multi-language support

## Documentation

**Update when:**
- Adding new features
- Changing configuration options
- Modifying installation process
- Fixing bugs that affect usage

**Files to update:**
- README.md - Overview and quick start
- FEATURES.md - New features
- CONFIGURATION.md - New config options
- Relevant guides in docs/

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Clarification on features
- Implementation advice
- General discussion

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

**Thank you for contributing!** 🙌
