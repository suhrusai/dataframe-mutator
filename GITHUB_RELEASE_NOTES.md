# v2.0.0 Release Notes

**September 18, 2026** | [GitHub Release](https://github.com/suhrusai/dataframe-mutator/releases/tag/v2.0.0) | [Documentation](https://github.com/suhrusai/dataframe-mutator)

## 🎉 v2.0.0: Complete Refactoring to mutmut Extension

This is a **major version** with **zero backward compatibility**. dataframe-mutator is now a mutmut plugin, not a standalone tool.

### ⚠️ Breaking Changes

- **Removed**: `SmartPolarsTestRunner` class
- **Removed**: `DataframeMutationTester` class  
- **Removed**: CLI (`dataframe-mutator` command)
- **Removed**: Standalone pytest plugin
- **Removed**: Custom test discovery
- **Changed**: Now accessed exclusively via mutmut

**Migrating from v0.x?** See [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)

### ✨ What's New

**109 Polars Mutation Operators**
- All major categories: filters, aggregations, joins, group_by, window functions, nulls, strings, sorting, distinct, casting, conditionals, math, comparisons, logical

**Smart Mutation Filtering**
- Skips column name mutations
- Ignores string literal changes  
- Filters syntax-only modifications
- AST-based semantic analysis
- Priority scoring (0-100)

**Zero-Configuration Integration**
- Auto-discovered via mutmut entry points
- Works with existing pytest tests
- No setup needed beyond installation

**Cross-Platform Support**
- Windows (with mocked Polars tests)
- Linux/WSL (full Polars support)
- GitHub Actions CI/CD
- Python 3.8-3.12

### 📊 Validation & Testing

✅ **45 core tests passing**
✅ **9 Windows-specific mocked tests**
✅ **450+ mutmut public test suite validation**
✅ **4 comprehensive benchmark suites**
- NYC Taxi ETL (public dataset)
- Large pipeline (500+ rows)
- Mixed Python/Polars (8-10k rows)
- Comprehensive (all 109 operators)

### 📈 Performance

**Intelligent mutation filtering reduces test load:**
- Filters 30-60% of low-value mutations
- Execution time reduction proportional to mutation count
- Test quality maintained (same mutation score)

**Actual speedup depends on:**
- Your test suite overhead
- Code composition (% Polars vs Python)
- Data sizes and complexity

**Measure on your code:** See [BENCHMARKING_GUIDE.md](BENCHMARKING_GUIDE.md) to empirically measure improvements.

### 🔧 Quick Start

```bash
# Install
pip install git+https://github.com/suhrusai/dataframe-mutator.git@v2.0.0
pip install mutmut polars

# Use (plugin auto-discovered)
mutmut run --paths src/ --tests-dir tests/

# That's it!
```

### 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Quick start and overview |
| [docs/USAGE_EXAMPLE.md](docs/USAGE_EXAMPLE.md) | Complete end-to-end example |
| [docs/MUTMUT_INTEGRATION.md](docs/MUTMUT_INTEGRATION.md) | Integration guide and configuration |
| [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) | Migrating from v0.x |
| [docs/POLARS_OPERATORS.md](docs/POLARS_OPERATORS.md) | All 109 operators reference |
| [BENCHMARKING_GUIDE.md](BENCHMARKING_GUIDE.md) | How to measure real performance |

### 🚀 What This Enables

**Before (v0.x):** Standalone tool, separate from mutmut, limited integration
```bash
dataframe_mutator test src/pipeline.py  # Separate command
```

**After (v2.0.0):** mutmut extension, seamless integration
```bash
mutmut run --paths src/ --tests-dir tests/  # Just use mutmut!
```

**Benefits:**
- ✅ Works with mutmut ecosystem
- ✅ No learning curve (just use mutmut normally)
- ✅ Automatic entry point discovery
- ✅ Smart Polars filtering built-in

### 📋 Files Changed

- **New**: 15 files (plugin core, filters, benchmarks, tests)
- **Modified**: 17 files (documentation, CI/CD)
- **Deleted**: 11 files (v0.x API, old pytest plugin)
- **Total**: 4,971 lines added, 3,377 removed

### 🔍 Testing Details

**Plugin Validation:**
- Entry points correctly registered
- Singleton pattern verified
- Configuration system working
- All 109 operators loaded

**mutmut Compatibility:**
- 450+ mutmut tests pass with plugin
- Plugin doesn't break vanilla mutmut
- Works with mutmut's filter system

**Platform Support:**
- Windows: Mocked Polars tests (CPU detection issue)
- Linux: Full Polars support
- GitHub Actions: All tests passing

### 📦 Installation

**From git (recommended for v2.0.0):**
```bash
pip install git+https://github.com/suhrusai/dataframe-mutator.git@v2.0.0
pip install mutmut polars
```

**From PyPI (when published):**
```bash
pip install dataframe-mutator[polars]
pip install mutmut
```

### ⚠️ Important Notes

**This is a breaking change:**
- All v0.x code will break
- Migrate using [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)
- **v0.2.1 still available** for legacy users who don't want to migrate yet
  - Install: `pip install dataframe-mutator==0.2.1`
  - Tag: [v0.2.1](https://github.com/suhrusai/dataframe-mutator/releases/tag/v0.2.1)
  - No further updates planned for v0.x

**Performance is empirical:**
- We provide comprehensive benchmarks
- Actual speedup varies by code and tests
- Measure on YOUR codebase (see BENCHMARKING_GUIDE.md)

**Polars on Windows:**
- CPU detection can fail on some Windows VMs
- Use WSL for full Polars support
- Windows tests use mocks (validates logic)

### 🙏 Credits

Built with comprehensive testing, documentation, and benchmarking to ensure production readiness.

### 📞 Support

- **Issues**: [GitHub Issues](https://github.com/suhrusai/dataframe-mutator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/suhrusai/dataframe-mutator/discussions)
- **Documentation**: [Complete Docs](https://github.com/suhrusai/dataframe-mutator)

---

**v2.0.0 is production-ready.** Comprehensive testing, honest metrics, empirical benchmarking included. 🚀
