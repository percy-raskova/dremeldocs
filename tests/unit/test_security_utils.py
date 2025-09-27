#!/usr/bin/env python3
"""
Unit tests for security_utils module.
"""

import tempfile
from pathlib import Path
import pytest
import os
from scripts.security_utils import (
    PathSecurityValidator,
    SecurityError,
    sanitize_filename,
    validate_json_input,
    safe_open,
)


class TestPathSecurityValidator:
    """Test path validation security features."""

    def test_valid_path_within_base(self, temp_dir):
        """Test that paths within base directory are allowed."""
        validator = PathSecurityValidator(base_dir=temp_dir)
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        result = validator.validate_path(test_file, must_exist=True)
        assert result == test_file.resolve()

    def test_path_traversal_blocked(self, temp_dir):
        """Test that path traversal is blocked."""
        # Temporarily clear the test environment variable
        old_pytest_var = os.environ.pop('PYTEST_CURRENT_TEST', None)
        
        try:
            validator = PathSecurityValidator(base_dir=temp_dir)
            
            with pytest.raises(SecurityError) as exc_info:
                validator.validate_path("/etc/passwd")
            
            assert "Path traversal detected" in str(exc_info.value)
        finally:
            # Restore the environment variable
            if old_pytest_var:
                os.environ['PYTEST_CURRENT_TEST'] = old_pytest_var

    def test_test_directories_allowed(self, temp_dir):
        """Test that pytest temp directories are allowed."""
        validator = PathSecurityValidator()  # Use project root

        # Create a pytest-style temp directory
        with tempfile.TemporaryDirectory(prefix="pytest-") as pytest_tmp:
            test_file = Path(pytest_tmp) / "test.txt"
            test_file.write_text("test")

            # Should not raise an error
            result = validator.validate_path(test_file, must_exist=True)
            assert result == test_file.resolve()

    def test_nonexistent_path_with_must_exist(self, temp_dir):
        """Test that nonexistent paths fail when must_exist=True."""
        validator = PathSecurityValidator(base_dir=temp_dir)
        fake_path = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            validator.validate_path(fake_path, must_exist=True)

    def test_validate_output_path_creates_parents(self, temp_dir):
        """Test that validate_output_path creates parent directories."""
        validator = PathSecurityValidator(base_dir=temp_dir)
        output_path = temp_dir / "nested" / "deep" / "output.txt"

        result = validator.validate_output_path(output_path)
        assert result == output_path.resolve()
        assert output_path.parent.exists()

    def test_invalid_path_raises_security_error(self):
        """Test that invalid paths raise SecurityError."""
        validator = PathSecurityValidator()

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_path("\x00invalid")

        assert "Invalid path" in str(exc_info.value)


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_removes_directory_separators(self):
        """Test that directory separators are removed."""
        result = sanitize_filename("../../etc/passwd")
        assert result == "____etc_passwd"

    def test_removes_null_bytes(self):
        """Test that null bytes are removed."""
        result = sanitize_filename("file\x00name.txt")
        assert result == "file_name.txt"  # Null bytes are replaced with underscore

    def test_removes_leading_dots(self):
        """Test that leading dots are removed."""
        result = sanitize_filename("...hidden")
        assert result == "_hidden"  # .. becomes _ and then leading dot is stripped

    def test_truncates_long_names(self):
        """Test that long filenames are truncated."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) == 255
        assert result.endswith(".txt")

    def test_handles_empty_filename(self):
        """Test that empty filenames become 'unnamed'."""
        result = sanitize_filename("")
        assert result == "unnamed"

    def test_preserves_normal_filename(self):
        """Test that normal filenames are preserved."""
        result = sanitize_filename("normal_file.txt")
        assert result == "normal_file.txt"


class TestValidateJsonInput:
    """Test JSON input validation."""

    def test_valid_dict_with_required_fields(self):
        """Test validation of valid dictionary with required fields."""
        data = {"field1": "value1", "field2": "value2"}
        result = validate_json_input(data, required_fields=["field1", "field2"])
        assert result is True

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValueError."""
        data = {"field1": "value1"}

        with pytest.raises(ValueError) as exc_info:
            validate_json_input(data, required_fields=["field1", "field2"])

        assert "Missing required fields" in str(exc_info.value)

    def test_non_dict_input(self):
        """Test that non-dictionary input raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_json_input([1, 2, 3])

        assert "Input must be a dictionary" in str(exc_info.value)

    def test_no_required_fields(self):
        """Test validation without required fields."""
        data = {"any": "data"}
        result = validate_json_input(data)
        assert result is True


class TestSafeOpen:
    """Test safe file opening function."""

    def test_safe_open_read_existing(self, temp_dir):
        """Test safe opening of existing file for reading."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        with safe_open(test_file, "r") as f:
            content = f.read()

        assert content == "content"

    def test_safe_open_write_creates_parents(self, temp_dir):
        """Test that safe_open creates parent directories for write mode."""
        output_file = temp_dir / "nested" / "output.txt"

        with safe_open(output_file, "w") as f:
            f.write("test content")

        assert output_file.exists()
        assert output_file.read_text() == "test content"

    def test_safe_open_blocks_traversal(self, temp_dir):
        """Test that safe_open blocks traversal attempts."""
        # Temporarily clear the test environment variable
        old_pytest_var = os.environ.pop('PYTEST_CURRENT_TEST', None)
        
        try:
            # Try to open a file outside the allowed directory
            with pytest.raises(SecurityError) as exc_info:
                with safe_open("/etc/passwd", "r"):
                    pass
            
            assert "Path traversal" in str(exc_info.value) or "outside" in str(exc_info.value)
        finally:
            # Restore the environment variable
            if old_pytest_var:
                os.environ['PYTEST_CURRENT_TEST'] = old_pytest_var

    def test_safe_open_test_directory(self):
        """Test that safe_open allows test directories."""
        with tempfile.TemporaryDirectory(prefix="pytest-") as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            with safe_open(test_file, "r") as f:
                content = f.read()

            assert content == "test"