"""Monkeypatch mutmut to use our Polars filter.

This runs before mutmut starts, injecting our filter into its core.
"""

import sys


def patch_mutmut():
    """Patch mutmut's mutation filter at import time."""
    try:
        from dataframe_mutator.mutmut_plugin import polars_filter

        # Hook into mutmut's mutation generation
        import mutmut.codegen

        # Store original generate_mutations
        original_generate = mutmut.codegen.generate_mutations

        _skip_count = 0
        _keep_count = 0

        def generate_mutations_filtered(from_mutant):
            """Generate mutations, filtering with polars_filter."""
            nonlocal _skip_count, _keep_count

            for mutation in original_generate(from_mutant):
                # Get the original and mutated code
                original = mutation.original_source
                mutated = mutation.mutated_source

                # Apply our filter
                if not polars_filter(original, mutated):
                    _skip_count += 1
                    continue  # Skip this mutation

                _keep_count += 1
                yield mutation

        # Replace the function
        mutmut.codegen.generate_mutations = generate_mutations_filtered
        print(f"[HOOK] Mutmut patched with Polars filter", file=sys.stderr)
        return True

    except Exception as e:
        print(f"[HOOK] Failed to patch mutmut: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


# Apply patch immediately on import
if __name__ != "__main__":
    patch_mutmut()
