# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-09-17

### Added
- **GitHub Actions CI/CD**
  - Automated test runs on Python 3.8-3.12
  - Code quality checks (ruff, black, mypy)
  - Coverage reporting to Codecov
  - Example project testing

- **Project Documentation**
  - CONTRIBUTING.md with developer guidelines
  - SECURITY.md for vulnerability reporting
  - CODE_OF_CONDUCT.md (Contributor Covenant)
  - CHANGELOG.md for release tracking

- **Performance Benchmarks**
  - BENCHMARKS.md documenting 6-10x speedup
  - Comparison vs vanilla mutmut
  - Scaling analysis

- **Example Showcase**
  - Sales ETL Pipeline example
  - 28 comprehensive tests
  - Detailed walkthrough documentation

### Improved
- Simplified README for better PyPI presentation
- Added CI status badge
- Enhanced project professionalism

## [0.1.0] - 2025-09-17

### Added
- **109 Production Operators** - Complete Polars API coverage
  - Filtering & Selection (12 operators)
  - Aggregations (15 operators)
  - Joins (7 operators)
  - Null Handling (10 operators)
  - String Operations (14 operators)
  - List Operations (8 operators)
  - DateTime Operations (8 operators)
  - Numeric Operations (12 operators)
  - Structural Operations (9 operators)
  - Sorting (5 operators)
  - Window Functions (15 operators)
  - I/O Operations (5 operators)
  - Metadata Operations (7 operators)
  - Advanced Operations (15 operators)
  - Type Operations (3 operators)

- **Smart Analysis Engine**
  - AST-aware filtering for false positive elimination
  - 6-10x faster testing vs vanilla mutmut
  - 99%+ false positive elimination rate
  - Semantic mutation detection

- **Core Features**
  - SmartPolarsTestRunner for easy integration
  - Comprehensive test suite (207+ tests)
  - 100% code coverage
  - Type hints throughout

- **Documentation & Examples**
  - Sales ETL Pipeline example with 28 tests
  - POLARS_FUNCTION_COVERAGE.md tracking
  - SMART_POLARS_APPROACH.md explanation
  - POLARS_OPERATORS.md reference guide
  - INTEGRATION_GUIDE.md for CI/CD setup

- **GitHub Actions Integration**
  - Automated PyPI publishing on releases
  - OIDC-based authentication support
  - Test and build workflows

### Features
- Mutation testing for Polars dataframe operations
- Production-grade code quality validation
- Catches boundary conditions, aggregation errors, data loss
- Python 3.8+ support

---

## Unreleased

### Planned
- Pandas backend support
- PySpark integration
- Custom mutation operator framework
- Performance benchmarking suite
- Web dashboard for mutation results
- Integration with more CI/CD platforms
