# dataframe-mutator Architecture: Polars Extension for mutmut

## Vision
dataframe-mutator is a **mutmut extension library** that adds Polars DataFrame support to Python's mutation testing ecosystem.

```
┌─────────────────────────────────────────┐
│           Regular Python Code           │
└────────────────┬────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │      mutmut        │  (General Python mutations)
        └────────┬───────────┘
                 │
                 ▼
    ┌──────────────────────────────┐
    │   dataframe-mutator plugin   │  (Polars-specific)
    │  ├─ Polars operators         │
    │  ├─ Smart filtering          │
    │  └─ Performance optimization │
    └──────────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │   Mutation Report  │
        │  (Optimized for    │
        │   Polars code)     │
        └────────────────────┘
```

## Architecture

### 1. **mutmut Integration Points**

#### A. Operator Registration
```python
# mutmut uses AST-based mutation operators
# dataframe-mutator registers Polars-specific operators:
- PolarsMutationOperator (base class)
- PolarsFilterOperator
- PolarsSelectOperator
- PolarsAggregationOperator
- ... (109 total operators)
```

#### B. Mutation Filtering
```python
# Hook into mutmut's mutation pipeline
class PolarsMutationFilter:
    def should_mutate(mutation):
        # Skip low-value mutations
        # - Column name mutations
        # - String literal mutations
        # - Syntax-only changes
```

#### C. Configuration
```python
# pyproject.toml
[tool.mutmut]
plugin = "dataframe_mutator"

[tool.dataframe-mutator]
skip_low_value_mutations = true
polars_operators = true
enable_semantic_analysis = true
```

### 2. **Package Structure**

```
dataframe-mutator/
├── src/dataframe_mutator/
│   ├── __init__.py
│   ├── mutmut_plugin.py          # Mutmut integration entry point
│   ├── operators/
│   │   ├── __init__.py
│   │   ├── base.py               # PolarsMutationOperator base
│   │   ├── filter.py             # Filter operators
│   │   ├── select.py             # Select operators
│   │   ├── aggregation.py        # Aggregation operators
│   │   └── ... (109 operators)
│   ├── filters/
│   │   ├── mutation_filter.py    # Polars-specific filtering
│   │   └── semantic_analyzer.py  # Smart analysis
│   ├── config.py                 # Configuration management
│   └── utils.py                  # Helper functions
├── tests/
│   ├── test_mutmut_integration.py
│   ├── test_operators.py
│   └── test_filtering.py
└── docs/
    ├── MUTMUT_INTEGRATION.md
    └── OPERATORS.md
```

### 3. **Key Components**

#### mutmut_plugin.py - Entry Point
```python
# Hook mutmut discovers via setup.py entry points
class DataframemutatorPlugin:
    def register_operators(mutmut):
        """Register all 109 Polars operators"""
        
    def register_filter(mutmut):
        """Register mutation filtering"""
        
    def configure(config):
        """Load configuration"""
```

#### operators/base.py - Operator Base Class
```python
class PolarsMutationOperator:
    """Base class for Polars mutations"""
    
    def matches(code_ast):
        """Does this mutation apply?"""
        
    def mutate(code_ast):
        """Generate mutated code"""
        
    def description():
        """Human-readable description"""
```

#### filters/mutation_filter.py - Smart Filtering
```python
class PolarsMutationFilter:
    def should_test_mutation(mutation, code):
        # Skip column names that exist in code
        # Skip string literals that aren't query-relevant
        # Skip syntax-only changes
        # Keep: logical changes, operator swaps, threshold changes
```

### 4. **Integration with mutmut CLI**

#### Option A: Plugin System (Recommended)
```bash
# mutmut discovers plugin via setup.py entry point
mutmut run --plugin dataframe-mutator

# Or automatically if installed
mutmut run
```

#### Option B: CLI Extension
```bash
# Wrapper CLI for convenience
mutmut-polars run my_polars_code.py

# Internally calls:
# mutmut run --plugin dataframe-mutator
```

#### Option C: Direct Integration
```bash
# Invoke through dataframe-mutator
dataframe-mutator benchmark my_polars_code.py
```

### 5. **setup.py Entry Points**

```python
entry_points={
    'mutmut.operators': [
        'polars = dataframe_mutator.operators:register_operators',
    ],
    'mutmut.filters': [
        'polars = dataframe_mutator.filters:register_filter',
    ],
}
```

### 6. **Configuration Schema**

```toml
# pyproject.toml
[tool.dataframe-mutator]
# Enable/disable Polars support
enabled = true

# Skip low-value mutations
skip_low_value_mutations = true

# Mutation filtering rules
filters = [
    "column_names",      # Skip column name mutations
    "string_literals",   # Skip non-query strings
    "syntax_only",       # Skip syntax-only changes
]

# Operators to include
operators = [
    "filters",
    "selections", 
    "aggregations",
    # ... all 109 by default
]

# Semantic analysis
enable_semantic_analysis = true
semantic_cache = ".mutmut-polars-cache"
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Remove custom mutation engine
- [ ] Create mutmut plugin interface
- [ ] Register Polars operators with mutmut
- [ ] Create basic filtering

### Phase 2: Integration (Week 2)
- [ ] Test with mutmut's test suite
- [ ] Implement configuration system
- [ ] Create mutmut hook system
- [ ] CLI wrapper (optional)

### Phase 3: Optimization (Week 3)
- [ ] Smart filtering implementation
- [ ] Semantic analysis
- [ ] Performance benchmarking
- [ ] Documentation

### Phase 4: Polish (Week 4)
- [ ] Full test coverage
- [ ] Documentation
- [ ] Examples
- [ ] Publish to PyPI

## Benefits

### For Users
- ✅ Works with standard mutmut workflow
- ✅ No learning curve (uses mutmut syntax)
- ✅ Polars optimization as opt-in feature
- ✅ Compatible with regular Python code
- ✅ Can be used with mutmut plugins

### For Maintainability
- ✅ Smaller codebase (reuse mutmut's mutation engine)
- ✅ Easier testing (reuse mutmut's test infrastructure)
- ✅ Future-proof (follows mutmut's updates)
- ✅ Community-aligned (contributes to mutmut ecosystem)

## Migration Path

### Current Users
```python
# Old (standalone)
from dataframe_mutator.polars import SmartPolarsTestRunner
tester = SmartPolarsTestRunner(test_command="pytest tests/")
results = tester.mutate_and_test("my_code.py")

# New (mutmut-integrated)
# Just use mutmut as normal!
# mutmut run

# Optional: Use Polars optimization
mutmut run --with-polars-optimization
```

## Success Criteria

- [ ] Works seamlessly with mutmut
- [ ] All 109 Polars operators registered
- [ ] Smart filtering reduces mutations by 80%+
- [ ] Compatible with regular Python code
- [ ] Full test coverage (>90%)
- [ ] Complete documentation
- [ ] PyPI publication

## References

- [mutmut Documentation](https://mutmut.readthedocs.io/)
- [mutmut Plugin System](https://mutmut.readthedocs.io/en/latest/plugins.html)
- [AST Mutation](https://mutmut.readthedocs.io/en/latest/how-it-works.html)
