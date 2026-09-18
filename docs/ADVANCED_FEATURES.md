# Advanced Features Guide

## Table of Contents

1. [CLI Tool](#cli-tool)
2. [Configuration Files](#configuration-files)
3. [Pytest Integration](#pytest-integration)
4. [Reports & Export](#reports--export)
5. [Baseline Tracking](#baseline-tracking)
6. [Integrations](#integrations)
7. [Parallel Testing](#parallel-testing)
8. [Custom Operators](#custom-operators)

---

## CLI Tool

### Installation

```bash
pip install dataframe-mutator[polars]
```

The CLI is automatically available:

```bash
dataframe-mutator --help
```

### Basic Usage

#### Analyze Code

```bash
dataframe-mutator analyze src/pipeline.py --tests tests/
```

**Options:**
- `--tests` - Test directory (default: `tests/`)
- `--output` - Format: `text`, `json`, `html` (default: `text`)
- `--threshold` - Mutation score threshold (0.0-1.0)
- `--parallel` - Use parallel testing (default: True)
- `--workers` - Number of parallel workers
- `--save-baseline` - Save results as baseline

#### Save Baseline

```bash
dataframe-mutator analyze src/ --save-baseline
```

#### Compare to Baseline

```bash
dataframe-mutator check src/ --tests tests/
```

#### Initialize Configuration

```bash
dataframe-mutator init
```

---

## Configuration Files

### TOML Configuration

Create `dataframe-mutator.toml`:

```toml
[dataframe-mutator]
source_files = ["src/pipeline.py"]
test_command = "pytest tests/"
skip_patterns = ["__pycache__", "*.test.py", ".git"]

# Thresholds
mutation_threshold = 0.85  # Fail if below 85%
min_mutations = 5          # Require at least 5 mutations

# Operators
operators = ["filter", "aggregation"]  # Only these
skip_operators = ["string_mutations"]

# Features
parallel = true
num_workers = 4
skip_low_value_mutations = true

# Output
output_format = "html"
output_dir = "mutation-results"
baseline_path = ".mutation-baseline.json"

# Integrations
github_annotations = true
slack_webhook = "https://hooks.slack.com/..."
```

### JSON Configuration

```json
{
  "mutation_threshold": 0.85,
  "parallel": true,
  "output_format": "html",
  "skip_patterns": ["__pycache__", ".git"]
}
```

### Load Configuration

```bash
dataframe-mutator analyze src/ --config custom-config.toml
```

---

## Pytest Integration

### Enable Mutation Testing

```bash
pytest --mutation tests/
```

**Options:**
- `--mutation` - Enable mutation testing
- `--mutation-source` - Source directory (default: `src/`)
- `--mutation-threshold` - Minimum score threshold

### Example Output

```
========================= Mutation Testing Results ==========================

✅ src/pipeline.py: 12 mutations (98.5% false pos avoided)
✅ src/utils.py: 5 mutations (99.2% false pos avoided)
⚠️ src/models.py: 0 mutations

========================= Pass ==========================
```

### Use as Fixture

```python
def test_with_mutation_testing(mutation_tester):
    """Test with mutation testing support."""
    results = mutation_tester.analyze_mutation_efficiency("src/pipeline.py")
    assert results['high_value_mutations'] >= 10
```

---

## Reports & Export

### JSON Export

```bash
dataframe-mutator analyze src/ --output json
```

**Output Structure:**

```json
{
  "timestamp": "2025-09-17T10:30:00",
  "config": {...},
  "results": {
    "src/pipeline.py": {
      "high_value_mutations": 12,
      "potential_false_positives_avoided": 98.5
    }
  },
  "summary": {
    "total_files": 1,
    "total_mutations": 12,
    "avg_false_positives_avoided": 98.5
  }
}
```

### HTML Reports

```bash
dataframe-mutator analyze src/ --output html
```

Generates `mutation-results/report.html` with:
- Summary metrics
- Per-file breakdown
- Visual formatting
- Shareable with team

---

## Baseline Tracking

### Save Baseline

```bash
dataframe-mutator analyze src/ --save-baseline
```

Creates `.mutation-baseline.json` with current mutation scores.

### Check Against Baseline

```bash
dataframe-mutator check src/ --tests tests/
```

**Output:**
```
✅ src/pipeline.py: 12 mutations (+1 vs baseline)
✅ src/utils.py: 5 mutations (same as baseline)
```

### Use in Python

```python
from dataframe_mutator.reports import BaselineTracker
from dataframe_mutator.config import MutationConfig

config = MutationConfig()
tracker = BaselineTracker(config)

# Save baseline
tracker.save_baseline(results)

# Load and compare
baseline = tracker.load_baseline()
comparison = tracker.compare(current_results)
```

---

## Integrations

### Slack Notifications

```python
from dataframe_mutator.integrations import SlackNotifier

notifier = SlackNotifier("https://hooks.slack.com/services/...")
notifier.notify(results, threshold=0.85)
```

**Configuration in TOML:**

```toml
[dataframe-mutator]
slack_webhook = "https://hooks.slack.com/..."
slack_on_fail_only = true
```

### GitHub Actions Annotations

```python
from dataframe_mutator.integrations import GitHubAnnotator

GitHubAnnotator.annotate_mutations(results)
```

**In GitHub Actions:**

```yaml
- name: Mutation Testing
  run: dataframe-mutator analyze src/ --github-annotations
```

### Custom Operators

```python
from dataframe_mutator.core import MutationOperator
from dataframe_mutator.integrations import CustomOperatorRegistry

class MyCustomMutation(MutationOperator):
    name = "custom_filter"
    description = "Mutates custom filter logic"
    
    def matches(self, node) -> bool:
        return ".my_filter(" in node
    
    def mutate(self, code: str) -> str:
        return code.replace(".my_filter(", ".alternative_filter(")

# Register
registry = CustomOperatorRegistry()
registry.register(MyCustomMutation)

# Use
operators = registry.load_operators()
```

---

## Parallel Testing

### Enable Parallel Mode

```bash
dataframe-mutator analyze src/ --parallel --workers 4
```

**Configuration:**

```toml
[dataframe-mutator]
parallel = true
num_workers = 4  # Or auto-detect: null
```

### Performance

- **Sequential:** 245s for 147 mutations
- **Parallel (4 workers):** 65s for 147 mutations
- **Speedup:** ~3.8x

---

## Advanced Usage

### Operator Suggestions

```python
from dataframe_mutator.integrations import OperatorSuggester

suggestions = OperatorSuggester.analyze_code("src/pipeline.py")
# {'filter_mutations': 5, 'aggregation_mutations': 3, ...}
```

### Multi-file Analysis

```bash
dataframe-mutator analyze src/pipeline.py src/utils.py src/models.py --output html
```

### Mutation Operator Statistics

```python
results = tester.analyze_mutation_efficiency("src/pipeline.py")

# Results include:
# - high_value_mutations: count
# - potential_false_positives_avoided: percentage
# - mutation_categories: breakdown by type
```

---

## Complete Example: CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Mutation Testing

on: [push, pull_request]

jobs:
  mutation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: pip install -e ".[dev,polars]"
      
      - name: Run mutation testing
        run: dataframe-mutator analyze src/ --output html --threshold 0.85
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: mutation-report
          path: mutation-results/report.html
      
      - name: Check baseline
        run: dataframe-mutator check src/ --tests tests/
```

### Configuration File

```toml
# dataframe-mutator.toml
[dataframe-mutator]
source_files = ["src/"]
test_command = "pytest tests/ -v"
mutation_threshold = 0.85
min_mutations = 10
parallel = true
num_workers = 4
output_format = "html"
slack_webhook = "${SLACK_WEBHOOK_URL}"
github_annotations = true
```

---

## Troubleshooting

### No Mutations Found

**Cause:** AST filtering too aggressive  
**Solution:** Check `skip_patterns`, ensure operators are enabled

### Slow Testing

**Cause:** Sequential mode  
**Solution:** Enable `--parallel --workers 4`

### Baseline Mismatch

**Cause:** Different test environment  
**Solution:** Regenerate baseline with `--save-baseline`

---

## Performance Tips

1. **Use parallel testing** - 3-8x faster
2. **Enable smart filtering** - Skip low-value mutations
3. **Exclude test directories** - Skip fixtures and helpers
4. **Use configuration files** - Avoid CLI args overhead
5. **Cache baseline** - Compare locally first

---

## API Reference

All features are available via Python API:

```python
from dataframe_mutator.polars import SmartPolarsTestRunner
from dataframe_mutator.config import MutationConfig
from dataframe_mutator.reports import HTMLReportGenerator, JSONExporter
from dataframe_mutator.integrations import SlackNotifier, GitHubAnnotator
```

See inline docstrings for complete API documentation.
