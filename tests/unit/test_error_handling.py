#!/usr/bin/env python3
"""
Unit tests for error_handling.py following Test-Driven Development principles.
Tests all error handling utilities, exception classes, and standardized patterns.
"""

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from error_handling import (
    ConfigurationError,
    DremelDocsError,
    FileProcessingError,
    ValidationError,
    graceful_exit,
    handle_file_operation_error,
    handle_json_error,
    log_processing_progress,
    safe_execute,
    safe_json_load,
    safe_json_save,
    setup_error_handling,
    validate_directory_path,
    validate_file_path,
    with_error_context,
)


class TestCustomExceptions:
    """Test custom exception hierarchy."""

    def test_dremeldocs_error_base(self):
        """Test base exception class."""
        error = DremelDocsError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_file_processing_error(self):
        """Test file processing error."""
        error = FileProcessingError("Failed to process file")
        assert str(error) == "Failed to process file"
        assert isinstance(error, DremelDocsError)

    def test_configuration_error(self):
        """Test configuration error."""
        error = ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"
        assert isinstance(error, DremelDocsError)

    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, DremelDocsError)

    def test_exception_inheritance(self):
        """Test exception inheritance chain."""
        errors = [
            FileProcessingError("test"),
            ConfigurationError("test"),
            ValidationError("test"),
        ]
        for error in errors:
            assert isinstance(error, DremelDocsError)
            assert isinstance(error, Exception)


class TestSafeExecute:
    """Test safe_execute function."""

    def test_successful_execution(self):
        """Test function executes successfully."""

        def good_func():
            return "success"

        result = safe_execute(good_func)
        assert result == "success"

    def test_execution_with_exception(self, capsys):
        """Test function handles exceptions."""

        def bad_func():
            raise ValueError("Test error")

        result = safe_execute(bad_func, fallback="default")
        assert result == "default"

        captured = capsys.readouterr()
        assert "⚠️  Warning:" in captured.out
        assert "ValueError" in captured.out

    def test_custom_error_message(self, capsys):
        """Test custom error message."""

        def bad_func():
            raise RuntimeError("Runtime issue")

        result = safe_execute(
            bad_func, fallback=None, error_message="Custom error occurred"
        )
        assert result is None

        captured = capsys.readouterr()
        assert "Custom error occurred" in captured.out
        assert "Runtime issue" in captured.out

    def test_silent_mode(self, capsys):
        """Test silent mode suppresses output."""

        def bad_func():
            raise Exception("Should not appear")

        result = safe_execute(bad_func, fallback="silent", silent=True)
        assert result == "silent"

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_no_fallback(self):
        """Test with no fallback value."""

        def bad_func():
            raise Exception("Error")

        result = safe_execute(bad_func)
        assert result is None

    def test_complex_return_type(self):
        """Test with complex return types."""

        def dict_func():
            return {"key": "value", "list": [1, 2, 3]}

        result = safe_execute(dict_func)
        assert result == {"key": "value", "list": [1, 2, 3]}


class TestValidateFilePath:
    """Test validate_file_path function."""

    def test_valid_existing_file(self, tmp_path):
        """Test validation of existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert validate_file_path(test_file, must_exist=True) is True

    def test_valid_path_not_required_to_exist(self, tmp_path):
        """Test validation when file doesn't need to exist."""
        test_file = tmp_path / "nonexistent.txt"

        assert validate_file_path(test_file, must_exist=False) is True

    def test_missing_required_file(self, tmp_path):
        """Test error when required file is missing."""
        test_file = tmp_path / "missing.txt"

        with pytest.raises(ValidationError, match="Required file does not exist"):
            validate_file_path(test_file, must_exist=True)

    def test_path_is_directory_not_file(self, tmp_path):
        """Test error when path is directory instead of file."""
        test_dir = tmp_path / "directory"
        test_dir.mkdir()

        with pytest.raises(ValidationError, match="Path is not a file"):
            validate_file_path(test_dir, must_exist=True)

    def test_missing_parent_directory(self):
        """Test error when parent directory doesn't exist."""
        test_file = Path("/nonexistent/directory/file.txt")

        with pytest.raises(ValidationError, match="Parent directory does not exist"):
            validate_file_path(test_file, must_exist=False)

    def test_string_path_conversion(self, tmp_path):
        """Test string paths are converted to Path objects."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Pass string instead of Path
        assert validate_file_path(str(test_file), must_exist=True) is True


class TestValidateDirectoryPath:
    """Test validate_directory_path function."""

    def test_valid_existing_directory(self, tmp_path):
        """Test validation of existing directory."""
        assert validate_directory_path(tmp_path, must_exist=True) is True

    def test_create_missing_directory(self, tmp_path, capsys):
        """Test creating directory when it doesn't exist."""
        new_dir = tmp_path / "new_directory"

        result = validate_directory_path(
            new_dir, must_exist=False, create_if_missing=True
        )
        assert result is True
        assert new_dir.exists()
        assert new_dir.is_dir()

        captured = capsys.readouterr()
        assert "✅ Created directory:" in captured.out

    def test_missing_required_directory(self, tmp_path):
        """Test error when required directory is missing."""
        missing_dir = tmp_path / "missing"

        with pytest.raises(ValidationError, match="Required directory does not exist"):
            validate_directory_path(
                missing_dir, must_exist=True, create_if_missing=False
            )

    def test_path_is_file_not_directory(self, tmp_path):
        """Test error when path is file instead of directory."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        with pytest.raises(ValidationError, match="Path is not a directory"):
            validate_directory_path(test_file, must_exist=True)

    def test_create_nested_directories(self, tmp_path):
        """Test creating nested directory structure."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        result = validate_directory_path(nested_dir, create_if_missing=True)
        assert result is True
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_create_directory_permission_error(self, tmp_path):
        """Test handling permission error when creating directory."""
        with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
            bad_dir = tmp_path / "cannot_create"

            with pytest.raises(ValidationError, match="Could not create directory"):
                validate_directory_path(bad_dir, create_if_missing=True)

    def test_string_path_conversion(self, tmp_path):
        """Test string paths are converted to Path objects."""
        assert validate_directory_path(str(tmp_path), must_exist=True) is True


class TestHandleJsonError:
    """Test handle_json_error function."""

    def test_json_syntax_error(self, capsys):
        """Test handling JSON syntax errors."""
        error = json.JSONDecodeError("Expecting comma", "", 10)
        test_path = Path("test.json")

        handle_json_error(error, test_path)

        captured = capsys.readouterr()
        assert "❌ JSON syntax error" in captured.out
        assert "Expecting comma" in captured.out
        assert "Check for missing commas, quotes, or brackets" in captured.out

    def test_json_decode_error(self, capsys):
        """Test handling JSON decode errors."""
        error = Exception("JSONDecoder error occurred")
        test_path = Path("bad.json")

        handle_json_error(error, test_path)

        captured = capsys.readouterr()
        assert "❌ JSON decode error" in captured.out
        assert "corrupted or not valid JSON" in captured.out

    def test_generic_json_error(self, capsys):
        """Test handling generic JSON errors."""
        error = Exception("Some other error")
        test_path = Path("file.json")

        handle_json_error(error, test_path)

        captured = capsys.readouterr()
        assert "❌ Error reading JSON file" in captured.out
        assert "Some other error" in captured.out


class TestHandleFileOperationError:
    """Test handle_file_operation_error function."""

    def test_permission_error(self, capsys):
        """Test handling permission errors."""
        error = PermissionError("Access denied")

        handle_file_operation_error(error, "reading", Path("protected.txt"))

        captured = capsys.readouterr()
        assert "❌ Permission denied reading file" in captured.out
        assert "Check file permissions and ownership" in captured.out

    def test_file_not_found_error(self, capsys):
        """Test handling file not found errors."""
        error = FileNotFoundError("No such file")

        handle_file_operation_error(error, "writing", Path("missing.txt"))

        captured = capsys.readouterr()
        assert "❌ File not found when writing" in captured.out
        assert "Verify the file path is correct" in captured.out

    def test_disk_space_error(self, capsys):
        """Test handling disk space errors."""
        error = OSError("No space left on device")

        handle_file_operation_error(error, "saving", Path("large.dat"))

        captured = capsys.readouterr()
        assert "❌ No disk space available" in captured.out

    def test_generic_os_error(self, capsys):
        """Test handling generic OS errors."""
        error = OSError("Device not ready")

        handle_file_operation_error(error, "opening", Path("device.txt"))

        captured = capsys.readouterr()
        assert "❌ System error opening file" in captured.out
        assert "Device not ready" in captured.out

    def test_unexpected_error(self, capsys):
        """Test handling unexpected errors."""
        error = RuntimeError("Unexpected issue")

        handle_file_operation_error(error, "processing", Path("data.txt"))

        captured = capsys.readouterr()
        assert "❌ Unexpected error processing file" in captured.out
        assert "Unexpected issue" in captured.out


class TestLogProcessingProgress:
    """Test log_processing_progress function."""

    def test_basic_progress_logging(self, capsys):
        """Test basic progress logging."""
        log_processing_progress(5, 10)

        captured = capsys.readouterr()
        assert "[  5/10] ( 50.0%) items" in captured.out

    def test_custom_item_name(self, capsys):
        """Test progress with custom item name."""
        log_processing_progress(25, 100, "threads")

        captured = capsys.readouterr()
        assert "[ 25/100] ( 25.0%) threads" in captured.out

    def test_zero_total(self, capsys):
        """Test handling zero total items."""
        log_processing_progress(0, 0, "files")

        captured = capsys.readouterr()
        assert "[  0/0] (  0.0%) files" in captured.out

    def test_complete_progress(self, capsys):
        """Test 100% progress."""
        log_processing_progress(50, 50, "documents")

        captured = capsys.readouterr()
        assert "[ 50/50] (100.0%) documents" in captured.out

    def test_formatting_alignment(self, capsys):
        """Test number formatting and alignment."""
        log_processing_progress(9, 1000, "records")

        captured = capsys.readouterr()
        assert "[  9/1000] (  0.9%) records" in captured.out


class TestGracefulExit:
    """Test graceful_exit function."""

    def test_success_exit(self, capsys):
        """Test successful exit."""
        with pytest.raises(SystemExit) as exc_info:
            graceful_exit("Operation completed successfully", exit_code=0)

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "✅ Operation completed successfully" in captured.out

    def test_error_exit(self, capsys):
        """Test error exit."""
        with pytest.raises(SystemExit) as exc_info:
            graceful_exit("Critical failure occurred", exit_code=1)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "❌ Critical failure occurred" in captured.out

    def test_custom_exit_codes(self):
        """Test various exit codes."""
        exit_codes = [2, 3, 127, 255]

        for code in exit_codes:
            with pytest.raises(SystemExit) as exc_info:
                graceful_exit(f"Exit with code {code}", exit_code=code)
            assert exc_info.value.code == code


class TestWithErrorContext:
    """Test with_error_context decorator."""

    def test_successful_function(self):
        """Test decorator with successful function."""

        @with_error_context("test operation")
        def good_function(x, y):
            return x + y

        result = good_function(2, 3)
        assert result == 5

    def test_function_with_exception(self, capsys):
        """Test decorator with failing function."""

        @with_error_context("calculation")
        def bad_function():
            raise ValueError("Division by zero")

        with pytest.raises(DremelDocsError, match="calculation failed"):
            bad_function()

        captured = capsys.readouterr()
        assert "❌ Error in calculation:" in captured.out
        assert "Division by zero" in captured.out

    def test_preserves_custom_exceptions(self):
        """Test decorator preserves DremelDocsError exceptions."""

        @with_error_context("custom operation")
        def custom_error_function():
            raise ValidationError("Invalid input")

        with pytest.raises(ValidationError, match="Invalid input"):
            custom_error_function()

    def test_debug_mode_traceback(self, capsys):
        """Test debug mode shows traceback."""
        original_argv = sys.argv.copy()
        sys.argv.append("--debug")

        try:

            @with_error_context("debug operation")
            def debug_function():
                raise RuntimeError("Debug error")

            with pytest.raises(DremelDocsError):
                debug_function()

            captured = capsys.readouterr()
            # Traceback would be printed if --debug is in sys.argv
            assert "❌ Error in debug operation:" in captured.out
        finally:
            sys.argv = original_argv

    def test_preserves_function_signature(self):
        """Test decorator preserves function arguments."""

        @with_error_context("signature test")
        def parameterized_function(a, b=10, *args, **kwargs):
            return {"a": a, "b": b, "args": args, "kwargs": kwargs}

        result = parameterized_function(1, 2, 3, 4, key="value")
        assert result == {"a": 1, "b": 2, "args": (3, 4), "kwargs": {"key": "value"}}


class TestSetupErrorHandling:
    """Test setup_error_handling function."""

    def test_setup_without_debug(self, capsys):
        """Test setup without debug mode."""
        setup_error_handling(debug=False)

        captured = capsys.readouterr()
        assert "Debug mode enabled" not in captured.out

    def test_setup_with_debug(self, capsys):
        """Test setup with debug mode."""
        setup_error_handling(debug=True)

        captured = capsys.readouterr()
        assert "🐛 Debug mode enabled" in captured.out

    def test_custom_excepthook_dremeldocs_error(self, capsys):
        """Test custom exception hook with DremelDocsError."""
        setup_error_handling(debug=False)

        # Simulate unhandled exception
        sys.excepthook(ValidationError, ValidationError("Test error"), None)

        captured = capsys.readouterr()
        assert "❌ Test error" in captured.out

    def test_custom_excepthook_generic_error(self, capsys):
        """Test custom exception hook with generic error."""
        setup_error_handling(debug=False)

        # Simulate unhandled exception
        sys.excepthook(RuntimeError, RuntimeError("Generic error"), None)

        captured = capsys.readouterr()
        assert "❌ Unexpected error: Generic error" in captured.out

    def test_custom_excepthook_with_debug(self, capsys):
        """Test exception hook with debug mode shows traceback."""

        setup_error_handling(debug=True)

        # Create a fake traceback
        try:
            raise RuntimeError("Debug test")
        except RuntimeError:
            exc_type, exc_value, exc_tb = sys.exc_info()

            # Capture the excepthook output
            sys.excepthook(exc_type, exc_value, exc_tb)

            captured = capsys.readouterr()
            assert "❌ Unexpected error: Debug test" in captured.out


class TestSafeJsonLoad:
    """Test safe_json_load function."""

    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file."""
        json_file = tmp_path / "valid.json"
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        json_file.write_text(json.dumps(data))

        result = safe_json_load(json_file)
        assert result == data

    def test_load_missing_file(self, tmp_path, capsys):
        """Test loading missing JSON file."""
        json_file = tmp_path / "missing.json"

        result = safe_json_load(json_file)
        assert result is None

        captured = capsys.readouterr()
        assert "❌ Validation error:" in captured.out
        assert "Required file does not exist" in captured.out

    def test_load_invalid_json(self, tmp_path, capsys):
        """Test loading invalid JSON file."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{invalid json content}")

        result = safe_json_load(json_file)
        assert result is None

        captured = capsys.readouterr()
        assert "❌ JSON" in captured.out

    def test_load_permission_error(self, tmp_path, capsys):
        """Test handling permission error when loading."""
        json_file = tmp_path / "protected.json"
        json_file.write_text('{"data": "value"}')

        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = safe_json_load(json_file)
            assert result is None

        captured = capsys.readouterr()
        assert "Permission denied" in captured.out

    def test_load_complex_json(self, tmp_path):
        """Test loading complex nested JSON."""
        json_file = tmp_path / "complex.json"
        data = {
            "nested": {"deep": {"structure": [1, 2, {"key": "value"}]}},
            "unicode": "émojis 🎉",
            "special": None,
            "boolean": True,
        }
        json_file.write_text(json.dumps(data, ensure_ascii=False))

        result = safe_json_load(json_file)
        assert result == data


class TestSafeJsonSave:
    """Test safe_json_save function."""

    def test_save_valid_json(self, tmp_path):
        """Test saving valid JSON data."""
        json_file = tmp_path / "output.json"
        data = {"key": "value", "list": [1, 2, 3]}

        result = safe_json_save(data, json_file)
        assert result is True
        assert json_file.exists()

        # Verify content
        saved_data = json.loads(json_file.read_text())
        assert saved_data == data

    def test_save_creates_directory(self, tmp_path):
        """Test saving creates parent directory if needed."""
        json_file = tmp_path / "new_dir" / "output.json"
        data = {"test": "data"}

        result = safe_json_save(data, json_file)
        assert result is True
        assert json_file.exists()
        assert json_file.parent.exists()

    def test_save_permission_error(self, tmp_path, capsys):
        """Test handling permission error when saving."""
        json_file = tmp_path / "readonly.json"
        data = {"test": "data"}

        with patch("builtins.open", side_effect=PermissionError("Cannot write")):
            result = safe_json_save(data, json_file)
            assert result is False

        captured = capsys.readouterr()
        assert "Permission denied" in captured.out

    def test_save_invalid_path(self, capsys):
        """Test handling invalid save path."""
        with patch("pathlib.Path.mkdir", side_effect=OSError("Invalid path")):
            json_file = Path("/invalid/path/file.json")
            data = {"test": "data"}

            result = safe_json_save(data, json_file)
            assert result is False

            captured = capsys.readouterr()
            assert "❌ Validation error:" in captured.out

    def test_save_unicode_content(self, tmp_path):
        """Test saving Unicode content."""
        json_file = tmp_path / "unicode.json"
        data = {"text": "Hello 世界 🌍", "symbols": "α β γ δ"}

        result = safe_json_save(data, json_file)
        assert result is True

        # Verify Unicode is preserved
        saved_text = json_file.read_text(encoding="utf-8")
        assert "世界" in saved_text
        assert "🌍" in saved_text
        assert "α β γ δ" in saved_text

    def test_save_formatting(self, tmp_path):
        """Test JSON formatting with indentation."""
        json_file = tmp_path / "formatted.json"
        data = {"nested": {"key": "value"}}

        result = safe_json_save(data, json_file)
        assert result is True

        # Check formatting
        content = json_file.read_text()
        assert "  " in content  # Has indentation
        assert content.count("\n") > 1  # Multiple lines


class TestErrorHandlingIntegration:
    """Integration tests for error handling utilities."""

    def test_combined_validation_and_loading(self, tmp_path):
        """Test combined file validation and loading."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"valid": "json"}')

        # Validate then load
        assert validate_file_path(json_file, must_exist=True) is True
        data = safe_json_load(json_file)
        assert data == {"valid": "json"}

    def test_error_context_with_safe_operations(self):
        """Test decorator with safe operations."""

        @with_error_context("integrated operation")
        def complex_operation():
            result = safe_execute(lambda: 10 / 2, fallback=0)
            if result == 0:
                raise ValidationError("Calculation failed")
            return result

        result = complex_operation()
        assert result == 5.0

    def test_full_error_pipeline(self, tmp_path, capsys):
        """Test complete error handling pipeline."""

        @with_error_context("pipeline test")
        def data_pipeline():
            # Create test data
            data_file = tmp_path / "pipeline.json"
            test_data = {"items": [1, 2, 3]}

            # Save data
            if not safe_json_save(test_data, data_file):
                raise FileProcessingError("Could not save data")

            # Load and process
            loaded_data = safe_json_load(data_file)
            if loaded_data is None:
                raise FileProcessingError("Could not load data")

            # Process items with progress
            total = len(loaded_data["items"])
            for i, item in enumerate(loaded_data["items"], 1):
                log_processing_progress(i, total, "items")

            return sum(loaded_data["items"])

        result = data_pipeline()
        assert result == 6

        captured = capsys.readouterr()
        assert "[  1/3]" in captured.out
        assert "[  2/3]" in captured.out
        assert "[  3/3]" in captured.out

    def test_nested_error_contexts(self):
        """Test nested error context decorators."""

        @with_error_context("outer operation")
        def outer():
            @with_error_context("inner operation")
            def inner():
                raise ValueError("Inner error")

            return inner()

        with pytest.raises(DremelDocsError, match="inner operation failed"):
            outer()

    def test_validation_chain(self, tmp_path):
        """Test chaining validation functions."""
        # Create test structure
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        config_file = base_dir / "config.json"
        config_file.write_text('{"setting": "value"}')

        # Validate directory and file
        assert validate_directory_path(base_dir, must_exist=True) is True
        assert validate_file_path(config_file, must_exist=True) is True

        # Load configuration
        config = safe_json_load(config_file)
        assert config == {"setting": "value"}


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_error_message(self, capsys):
        """Test handling empty error messages."""
        error = Exception("")
        handle_json_error(error, Path("test.json"))

        captured = capsys.readouterr()
        assert "❌" in captured.out

    def test_very_long_path(self, capsys):
        """Test handling very long file paths."""
        long_path = Path("/" + "a" * 200 + "/file.json")
        error = FileNotFoundError("Not found")

        handle_file_operation_error(error, "reading", long_path)

        captured = capsys.readouterr()
        assert "❌" in captured.out
        assert "reading" in captured.out

    def test_none_values_in_safe_execute(self):
        """Test safe_execute with None returns."""

        def returns_none():
            return None

        result = safe_execute(returns_none, fallback="default")
        assert result is None  # Should return None, not fallback

    def test_circular_reference_in_json(self, tmp_path, capsys):
        """Test handling circular references in JSON save."""
        # Create circular reference
        data: Any = {"key": "value"}
        data["self"] = data

        json_file = tmp_path / "circular.json"
        result = safe_json_save(data, json_file)
        assert result is False

        captured = capsys.readouterr()
        assert "❌" in captured.out

    def test_unicode_in_error_messages(self, capsys):
        """Test Unicode in error messages."""
        error = ValueError("Error with émoji 🎉")

        def unicode_error():
            raise error

        safe_execute(unicode_error, fallback=None)

        captured = capsys.readouterr()
        assert "émoji 🎉" in captured.out

    def test_zero_byte_file(self, tmp_path):
        """Test handling zero-byte files."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        result = safe_json_load(empty_file)
        assert result is None  # Should fail to parse empty file

    def test_symlink_validation(self, tmp_path):
        """Test validating symlinked files."""
        real_file = tmp_path / "real.txt"
        real_file.write_text("content")

        symlink = tmp_path / "link.txt"
        symlink.symlink_to(real_file)

        assert validate_file_path(symlink, must_exist=True) is True

    def test_special_characters_in_paths(self, tmp_path):
        """Test handling special characters in file paths."""
        special_dir = tmp_path / "dir with spaces & special!@#"
        special_dir.mkdir()

        assert validate_directory_path(special_dir, must_exist=True) is True

        special_file = special_dir / "file (with) [brackets].json"
        special_file.write_text('{"test": true}')

        assert validate_file_path(special_file, must_exist=True) is True
        data = safe_json_load(special_file)
        assert data == {"test": True}


class TestConcurrency:
    """Test thread safety and concurrency handling."""

    def test_concurrent_safe_execute(self):
        """Test safe_execute with concurrent calls."""
        import threading

        results = []

        def thread_function(value):
            def func():
                return value * 2

            result = safe_execute(func)
            results.append(result)

        threads = []
        for i in range(10):
            t = threading.Thread(target=thread_function, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 10
        assert sorted(results) == [i * 2 for i in range(10)]

    def test_concurrent_json_operations(self, tmp_path):
        """Test concurrent JSON save/load operations."""
        import threading

        def save_load_cycle(index):
            file_path = tmp_path / f"concurrent_{index}.json"
            data = {"index": index, "value": index * 10}

            # Save
            assert safe_json_save(data, file_path) is True

            # Load
            loaded = safe_json_load(file_path)
            assert loaded == data

        threads = []
        for i in range(5):
            t = threading.Thread(target=save_load_cycle, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify all files exist
        for i in range(5):
            assert (tmp_path / f"concurrent_{i}.json").exists()


class TestMemoryAndPerformance:
    """Test memory efficiency and performance."""

    def test_large_json_handling(self, tmp_path):
        """Test handling large JSON files."""
        large_data = {f"key_{i}": {"value": i, "data": "x" * 100} for i in range(1000)}

        json_file = tmp_path / "large.json"

        # Save large file
        assert safe_json_save(large_data, json_file) is True

        # Load large file
        loaded = safe_json_load(json_file)
        assert loaded == large_data

    def test_many_progress_updates(self, capsys):
        """Test many progress updates don't cause issues."""
        for i in range(1, 101):
            log_processing_progress(i, 100, "items")

        captured = capsys.readouterr()
        assert "[100/100] (100.0%)" in captured.out

    def test_recursive_directory_creation(self, tmp_path):
        """Test deep recursive directory creation."""
        deep_path = tmp_path
        for i in range(20):
            deep_path = deep_path / f"level_{i}"

        assert validate_directory_path(deep_path, create_if_missing=True) is True
        assert deep_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
