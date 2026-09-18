"""Mutmut configuration to enable Polars mutation filtering."""

def init():
    """Initialize mutmut with Polars filter."""
    try:
        from dataframe_mutator.mutmut_plugin import polars_filter

        # Register the filter
        from mutmut import config
        mutmut_config = config.config()

        # Mutmut uses a hook-based system for filters
        # We need to patch the should_mutate check
        print("[mutmut config] Polars filter loaded")
        return polars_filter
    except Exception as e:
        print(f"[mutmut config] Failed to load Polars filter: {e}")
        return None
