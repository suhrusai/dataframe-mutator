"""Configuration management for dataframe-mutator."""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Try to import tomllib (Python 3.11+)
try:
    import tomllib
except ImportError:
    tomllib = None


@dataclass
class MutationConfig:
    """Configuration for mutation testing."""

    # Paths
    source_files: List[str] = field(default_factory=list)
    test_command: str = "pytest tests/"
    skip_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "*.pyc", ".git"])

    # Thresholds
    mutation_threshold: float = 0.85  # Fail if below 85%
    min_mutations: int = 5  # Require at least 5 mutations

    # Operators
    operators: Optional[List[str]] = None  # None = all operators
    skip_operators: List[str] = field(default_factory=list)

    # Features
    skip_low_value_mutations: bool = True
    parallel: bool = True
    num_workers: Optional[int] = None  # None = auto (cpu_count)

    # Output
    output_format: str = "text"  # text, json, html
    output_dir: str = "mutation-results"
    save_baseline: bool = False
    baseline_path: str = ".mutation-baseline.json"

    # Integrations
    github_annotations: bool = False
    slack_webhook: Optional[str] = None
    slack_on_fail_only: bool = True

    # Advanced
    timeout_per_test: Optional[int] = None  # Seconds
    max_mutations_per_file: Optional[int] = None

    @classmethod
    def from_toml(cls, path: str = "dataframe-mutator.toml") -> "MutationConfig":
        """Load configuration from TOML file."""
        config_path = Path(path)
        if not config_path.exists():
            return cls()

        try:
            # Try Python 3.11+ tomllib first
            if tomllib:
                with open(config_path, "rb") as f:
                    data = tomllib.load(f)
            else:
                # Fallback for older Python
                import tomli
                with open(config_path, "rb") as f:
                    data = tomli.load(f)

            config_data = data.get("dataframe-mutator", {})
            return cls(**config_data)
        except Exception as e:
            logger.warning(f"Could not load config from {path}: {e}")
            return cls()

    @classmethod
    def from_json(cls, path: str) -> "MutationConfig":
        """Load configuration from JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            logger.warning(f"Could not load config from {path}: {e}")
            return cls()

    def to_json(self, path: str) -> None:
        """Save configuration to JSON file."""
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
