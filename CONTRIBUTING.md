# Contributing to dataframe-mutator

Thank you for your interest in contributing! We welcome contributions of all kinds.

## Getting Started

### Set up development environment

```bash
# Clone the repository
git clone https://github.com/suhrusai/dataframe-mutator.git
cd dataframe-mutator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev,polars]"
```

### Run tests locally

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/dataframe_mutator

# Run specific test file
pytest tests/test_smart_analysis.py -v
```

### Check code quality

```bash
# Format with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/ --fix

# Type check with mypy
mypy src/ --ignore-missing-imports
```

## Development Workflow

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new features
   - Update docstrings
   - Ensure all tests pass

3. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: describe what you did"
   ```

4. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Types of Contributions

### 🐛 Bug Reports
- Use GitHub Issues with clear reproduction steps
- Include Python version, Polars version, and error traceback
- Provide minimal example code

### ✨ Feature Requests
- Open an Issue with clear use case
- Explain why the feature would be useful
- Include example usage

### 📖 Documentation
- Fix typos and unclear explanations
- Add examples for complex features
- Improve docstrings

### 🔧 Code Improvements
- Add new mutation operators
- Improve existing operators
- Optimize performance
- Add test coverage

### 📦 New Backend Support
- Pandas integration
- PySpark support
- Other dataframe libraries

## Mutation Operator Guidelines

Adding a new operator? Follow this structure:

```python
from dataframe_mutator.core import MutationOperator

class MyNewMutation(MutationOperator):
    """Clear description of what this operator mutates."""
    
    name = "my_new_mutation"
    description = "Mutates [specific operation]"
    
    def matches(self, node) -> bool:
        """Return True if this operator should mutate the node."""
        if isinstance(node, str):
            return ".my_operation(" in node
        return False
    
    def mutate(self, node: str) -> str:
        """Return the mutated code."""
        return node.replace(".my_operation(", ".alternative_operation(")

# Add tests
class TestMyNewMutation:
    def test_basic_mutation(self):
        """Ensure mutation is applied correctly."""
        ...
    
    def test_detects_semantic_change(self):
        """Verify mutation changes behavior."""
        ...
```

## Testing Requirements

- All new features must have tests
- Tests should cover happy path and edge cases
- Maintain or improve code coverage
- Tests should validate mutation detection

## Code Style

- Follow PEP 8
- Use type hints (Python 3.8+)
- Black for formatting (line length: 100)
- Ruff for linting

## Documentation Requirements

- Update README.md if adding features
- Add docstrings to all public functions
- Include examples in complex features
- Update CHANGELOG.md

## PR Guidelines

- Keep PRs focused (one feature per PR)
- Write clear PR description
- Link related issues
- Ensure all CI checks pass
- Request review from maintainers

## Community

- Be respectful and inclusive
- Follow the Code of Conduct
- Help other contributors
- Share feedback constructively

## Questions?

- 💬 Open an Issue for questions
- 📖 Check existing documentation
- 🔍 Search closed Issues for answers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making dataframe-mutator better!** 🚀
