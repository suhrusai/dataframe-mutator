"""Tests for mutmut plugin integration.

Tests verify that dataframe-mutator integrates properly with mutmut
as a plugin and provides Polars-specific mutation testing.
"""

from dataframe_mutator.mutmut_plugin import DataframeMutatorPlugin, get_plugin


class TestPluginInitialization:
    """Test plugin initialization and registration."""

    def test_plugin_creation(self):
        """Test creating a plugin instance."""
        plugin = DataframeMutatorPlugin()
        assert plugin is not None
        assert plugin.operators_registered is False
        assert plugin.filter_registered is False

    def test_plugin_singleton(self):
        """Test get_plugin returns singleton instance."""
        plugin1 = get_plugin()
        plugin2 = get_plugin()
        assert plugin1 is plugin2

    def test_plugin_string_representation(self):
        """Test plugin string representation."""
        plugin = DataframeMutatorPlugin()
        str_repr = str(plugin)
        assert "DataframeMutatorPlugin" in str_repr
        assert "Operators" in str_repr
        assert "Filter" in str_repr


class TestPluginConfiguration:
    """Test plugin configuration."""

    def test_configure_with_empty_config(self):
        """Test configuring with empty dictionary."""
        plugin = DataframeMutatorPlugin()
        plugin.configure({})
        assert plugin.config == {}

    def test_configure_with_skip_low_value(self):
        """Test configuration with skip_low_value_mutations."""
        plugin = DataframeMutatorPlugin()
        config = {"skip_low_value_mutations": True}
        plugin.configure(config)
        assert plugin.config["skip_low_value_mutations"] is True

    def test_configure_with_semantic_analysis(self):
        """Test configuration with semantic analysis."""
        plugin = DataframeMutatorPlugin()
        config = {"enable_semantic_analysis": True}
        plugin.configure(config)
        assert plugin.config["enable_semantic_analysis"] is True


class TestPluginFactoryMethod:
    """Test plugin factory method."""

    def test_create_factory_method(self):
        """Test factory method creates instance."""
        plugin = DataframeMutatorPlugin.create()
        assert isinstance(plugin, DataframeMutatorPlugin)
        assert not plugin.operators_registered
        assert not plugin.filter_registered
