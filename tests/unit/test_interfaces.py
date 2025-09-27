#!/usr/bin/env python3
"""
Unit tests for interfaces module.
"""

import pytest
from scripts.interfaces import (
    get_nlp_instance,
    clean_social_text,
    MODEL_TYPE,
    NLP_CONFIG,
    TextProcessorInterface,
    TagExtractorInterface,
    NLPProcessorInterface,
)


class TestNLPSingleton:
    """Test NLP singleton pattern."""

    def test_get_nlp_instance_returns_same_instance(self):
        """Test that get_nlp_instance returns the same instance."""
        try:
            nlp1 = get_nlp_instance()
            nlp2 = get_nlp_instance()
            assert nlp1 is nlp2
        except OSError:
            pytest.skip("SpaCy model not available")

    def test_nlp_instance_has_correct_config(self):
        """Test that NLP instance has correct configuration."""
        try:
            nlp = get_nlp_instance()
            assert nlp.max_length == NLP_CONFIG["max_length"]
        except OSError:
            pytest.skip("SpaCy model not available")

    def test_model_type_constant(self):
        """Test that MODEL_TYPE is defined."""
        # MODEL_TYPE is set dynamically based on which model loads
        # It will be one of: "large", "transformer", "medium", "small"
        assert MODEL_TYPE in ["large", "transformer", "medium", "small"]

    def test_nlp_config_structure(self):
        """Test that NLP_CONFIG has expected structure."""
        assert "max_length" in NLP_CONFIG
        assert NLP_CONFIG["max_length"] == 2_000_000


class TestCleanSocialText:
    """Test social text cleaning function."""

    def test_removes_urls(self):
        """Test that URLs are removed."""
        text = "Check this https://example.com and www.test.com"
        result = clean_social_text(text)
        assert "https://example.com" not in result
        assert "www.test.com" not in result

    def test_removes_mentions(self):
        """Test that mentions are removed."""
        text = "Hey @user1 and @user2, what's up?"
        result = clean_social_text(text)
        assert "@user1" not in result
        assert "@user2" not in result
        assert "Hey and , what's up?" == result

    def test_removes_hashtag_symbols(self):
        """Test that hashtag symbols are removed but words kept."""
        text = "This is #important and #revolutionary"
        result = clean_social_text(text)
        assert "#" not in result
        assert "important" in result
        assert "revolutionary" in result

    def test_normalizes_whitespace(self):
        """Test that whitespace is normalized."""
        text = "Too    many     spaces\n\n\nand\tlines"
        result = clean_social_text(text)
        assert result == "Too many spaces and lines"

    def test_handles_empty_string(self):
        """Test that empty strings are handled."""
        result = clean_social_text("")
        assert result == ""

    def test_complex_cleaning(self):
        """Test complex text with multiple elements."""
        text = """
        Hey @everyone! Check out https://example.com/article
        It's about #politics and #theory. Also see www.test.org

        Too    many   spaces   here.
        """
        result = clean_social_text(text)

        assert "@everyone" not in result
        assert "https://" not in result
        assert "www." not in result
        assert "#" not in result
        assert "politics" in result
        assert "theory" in result
        # Check whitespace normalization
        assert "  " not in result  # No double spaces


class TestAbstractInterfaces:
    """Test abstract interface classes."""

    def test_text_processor_interface_is_abstract(self):
        """Test that TextProcessorInterface is abstract."""
        with pytest.raises(TypeError):
            TextProcessorInterface()

    def test_tag_extractor_interface_is_abstract(self):
        """Test that TagExtractorInterface is abstract."""
        with pytest.raises(TypeError):
            TagExtractorInterface()

    def test_nlp_processor_interface_is_abstract(self):
        """Test that NLPProcessorInterface is abstract."""
        with pytest.raises(TypeError):
            NLPProcessorInterface()

    def test_can_inherit_from_interfaces(self):
        """Test that classes can inherit from interfaces."""

        class ConcreteProcessor(TextProcessorInterface):
            def process(self, text: str):
                return text.upper()

        processor = ConcreteProcessor()
        result = processor.process("test")
        assert result == "TEST"


class TestInterfacesIntegration:
    """Test interfaces module integration."""

    def test_all_exports_available(self):
        """Test that all expected exports are available."""
        from scripts import interfaces

        # Check exports
        assert hasattr(interfaces, "TextProcessorInterface")
        assert hasattr(interfaces, "TagExtractorInterface")
        assert hasattr(interfaces, "NLPProcessorInterface")
        assert hasattr(interfaces, "MODEL_TYPE")
        assert hasattr(interfaces, "NLP_CONFIG")
        assert hasattr(interfaces, "get_nlp_instance")
        assert hasattr(interfaces, "clean_social_text")

    def test_no_circular_imports(self):
        """Test that importing interfaces doesn't cause circular imports."""
        # This test passes if it doesn't raise ImportError
        import scripts.interfaces
        import scripts.nlp_core
        import scripts.tag_extraction
        import scripts.text_utilities

        # All modules should be importable
        assert scripts.interfaces
        assert scripts.nlp_core
        assert scripts.tag_extraction
        assert scripts.text_utilities