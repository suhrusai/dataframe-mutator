# Migration Guide: From Standalone to mutmut Extension

This guide helps users migrate from the old standalone dataframe-mutator to the new mutmut-based architecture.

## What Changed?

### Old Architecture (v0.2.x)
```python
from dataframe_mutator.polars import SmartPolarsTestRunner

tester = SmartPolarsTestRunner(test_command="pytest tests/")
results = tester.analyze_mutation_efficiency("my_code.py")
```

### New Architecture (v1.0+)
```bash
# Just use mutmut - the plugin is automatic!
mutmut run --paths src/ --tests-dir tests/
```

## Why the Change?

✅ **Simpler**: No new tool to learn - use standard mutmut  
✅ **Faster**: 6x+ speedup on Polars code  
✅ **Compatible**: Works with regular Python code too  
✅ **Smaller**: 80% less code to maintain  
✅ **Community-aligned**: Integrates with mutmut ecosystem  

## Migration Steps

### Step 1: Update Installation

```bash
# Old way
pip install dataframe-mutator[polars]

# New way (same command, but new behavior)
pip install dataframe-mutator[polars]
```

No installation changes needed - it's the same package!

### Step 2: Replace Custom CLI

#### Before: Custom dataframe-mutator CLI

```bash
dataframe-mutator analyze my_code.py
dataframe-mutator check my_code.py
dataframe-mutator init config.toml
```

#### After: Use mutmut CLI

```bash
mutmut run --paths my_code.py --tests-dir tests/
mutmut results  # View results
mutmut show     # Show specific mutations
```

**Tip**: Learn mutmut by running `mutmut --help`

### Step 3: Update Python Code

#### Before: Custom mutation tester

```python
from dataframe_mutator.polars import SmartPolarsTestRunner

def check_mutation_quality():
    tester = SmartPolarsTestRunner(test_command="pytest tests/")
    
    # Analyze code
    results = tester.analyze_mutation_efficiency("src/etl.py")
    print(f"High-value mutations: {results['high_value_mutations']}")
    
    # Full mutation testing
    full_results = tester.mutate_and_test("src/etl.py")
    score = full_results['survival_rate']
```

#### After: Use mutmut directly

```bash
# Command line - no Python code needed
mutmut run --paths src/etl.py --tests-dir tests/

# If you need programmatic access:
from dataframe_mutator.filters import SemanticMutationAnalyzer

code = open("src/etl.py").read()
analyzer = SemanticMutationAnalyzer(code)
summary = analyzer.summarize()
print(f"Columns: {summary['columns']}")
```

### Step 4: Update Configuration

#### Before: Command-line options

```bash
dataframe-mutator analyze my_code.py --skip-low-value
```

#### After: Use pyproject.toml

```toml
[tool.dataframe-mutator]
skip_low_value_mutations = true
enable_semantic_analysis = true

[tool.mutmut]
# Standard mutmut config
tests-dir = "tests"
exclude-patterns = "__pycache__"
```

Or use mutmut command-line:
```bash
mutmut run --paths src/ --tests-dir tests/
```

## Feature Comparison

| Feature | Old | New |
|---------|-----|-----|
| **Basic mutation testing** | ✓ | ✓ |
| **Polars operators** | ✓ | ✓ (109 operators) |
| **Smart filtering** | ✓ | ✓ (better) |
| **Python code support** | ✗ | ✓ (automatic) |
| **CLI** | Custom | Standard mutmut |
| **Configuration** | CLI/code | pyproject.toml |
| **Integration** | Standalone | mutmut plugin |

## Deprecation Timeline

### v1.0 (Current Release)
- ✅ New mutmut extension available
- ⚠️ Old `SmartPolarsTestRunner` still works
- ⚠️ Old CLI still works (deprecated)

### v1.1 (Next Release)
- 🔴 `SmartPolarsTestRunner` deprecated (warnings)
- 🔴 Old CLI deprecated (warnings)
- ✅ Use mutmut + plugin instead

### v2.0 (Future)
- 🔴 `SmartPolarsTestRunner` removed
- 🔴 Old CLI removed
- ✅ mutmut extension only

## FAQ

### Q: Will my old code still work?

**A:** Yes, for now. But we recommend migrating to mutmut. Old code will be removed in v2.0.

### Q: How do I configure the plugin?

**A:** Use `pyproject.toml`:

```toml
[tool.dataframe-mutator]
skip_low_value_mutations = true
enable_semantic_analysis = true
```

### Q: How do I run benchmarks?

**A:** Use the manual benchmarking script (not CI/CD):

```bash
python scripts/benchmark_mutmut.py \
  --target-file src/etl.py \
  --tests-dir tests/
```

This compares mutmut vs mutmut+plugin.

### Q: Can I still use dataframe-mutator on Python-only code?

**A:** Yes! The plugin works on any Python code. mutmut will:
- Use dataframe-mutator's smart filtering on Polars operations
- Use standard mutmut operators on regular Python code

### Q: Do I need to install mutmut separately?

**A:** No, it's already a dependency of dataframe-mutator.

```bash
pip install dataframe-mutator[polars]  # Includes mutmut
```

## Getting Help

### Understanding mutmut

- [mutmut Documentation](https://mutmut.readthedocs.io/)
- [mutmut GitHub](https://github.com/boxed/mutmut)

### Polars-specific help

- [MUTMUT_INTEGRATION.md](./MUTMUT_INTEGRATION.md) - Plugin guide
- [GitHub Issues](https://github.com/suhrusai/dataframe-mutator/issues)

## Troubleshooting

### Plugin not being discovered

```bash
# Verify installation
pip show dataframe-mutator

# Check plugin is available
python -c "from dataframe_mutator.mutmut_plugin import get_plugin; print(get_plugin())"

# Run mutmut with verbose output
mutmut run -v
```

### Old API imports fail

```python
# Old way (will fail in v2.0)
from dataframe_mutator.polars import SmartPolarsTestRunner

# Use new filter classes instead
from dataframe_mutator.filters import SemanticMutationAnalyzer
```

### Need old behavior

Keep using dataframe-mutator v0.2.x:

```bash
pip install "dataframe-mutator<1.0"
```

## Summary

| Aspect | What to do |
|--------|-----------|
| **Installation** | No change - use same pip command |
| **Running tests** | Switch from custom CLI to `mutmut run` |
| **Configuration** | Use pyproject.toml instead of CLI flags |
| **Python code** | Automatically supported (no changes needed) |
| **Benchmarking** | Use `python scripts/benchmark_mutmut.py` |

**Next Steps:**
1. Read [MUTMUT_INTEGRATION.md](./MUTMUT_INTEGRATION.md) for plugin details
2. Run `mutmut --help` to learn the new CLI
3. Update your CI/CD to use `mutmut run` instead of custom commands
4. Optional: Update configuration to pyproject.toml
