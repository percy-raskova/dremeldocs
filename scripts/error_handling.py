#!/usr/bin/env python3
"""
Standardized error handling utilities for DremelDocs scripts.
Provides consistent error logging and graceful degradation patterns.
"""

import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


class DremelDocsError(Exception):
    """Base exception for DremelDocs-specific errors."""

    pass


class FileProcessingError(DremelDocsError):
    """Raised when file processing operations fail."""

    pass


class ConfigurationError(DremelDocsError):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(DremelDocsError):
    """Raised when input validation fails."""

    pass


def safe_execute(
    func: Callable[[], T],
    fallback: Optional[T] = None,
    error_message: Optional[str] = None,
    silent: bool = False,
) -> Optional[T]:
    """
    Safely execute a function with standardized error handling.

    Args:
        func: Function to execute
        fallback: Value to return if function fails
        error_message: Custom error message to display
        silent: If True, suppress error output

    Returns:
        Function result or fallback value
    """
    try:
        return func()
    except Exception as e:
        if not silent:
            msg = error_message or f"Operation failed: {type(e).__name__}"
            print(f"⚠️  Warning: {msg}: {e}")
        return fallback


def validate_file_path(path: Path, must_exist: bool = True) -> bool:
    """
    Validate file path with standardized error messages.

    Args:
        path: Path to validate
        must_exist: Whether the file must already exist

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(path, Path):
        path = Path(path)

    # Check if parent directory exists
    if not path.parent.exists():
        raise ValidationError(f"Parent directory does not exist: {path.parent}")

    if must_exist and not path.exists():
        raise ValidationError(f"Required file does not exist: {path}")

    if must_exist and not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    return True


def validate_directory_path(
    path: Path, must_exist: bool = True, create_if_missing: bool = False
) -> bool:
    """
    Validate directory path with standardized error messages.

    Args:
        path: Path to validate
        must_exist: Whether the directory must already exist
        create_if_missing: Create directory if it doesn't exist

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(path, Path):
        path = Path(path)

    if not path.exists():
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {path}")
                return True
            except OSError as e:
                raise ValidationError(f"Could not create directory {path}: {e}")
        elif must_exist:
            raise ValidationError(f"Required directory does not exist: {path}")

    if path.exists() and not path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")

    return True


def handle_json_error(e: Exception, file_path: Path) -> None:
    """
    Standardized JSON error handling with helpful messages.

    Args:
        e: Exception that occurred
        file_path: Path to the JSON file that failed
    """
    if "Expecting" in str(e):
        print(f"❌ JSON syntax error in {file_path}:")
        print(f"   {e}")
        print("   Hint: Check for missing commas, quotes, or brackets")
    elif "decoder" in str(e).lower():
        print(f"❌ JSON decode error in {file_path}:")
        print("   File may be corrupted or not valid JSON")
    else:
        print(f"❌ Error reading JSON file {file_path}: {e}")


def handle_file_operation_error(e: Exception, operation: str, file_path: Path) -> None:
    """
    Standardized file operation error handling.

    Args:
        e: Exception that occurred
        operation: Description of the operation (e.g., "reading", "writing")
        file_path: Path to the file that failed
    """
    if isinstance(e, PermissionError):
        print(f"❌ Permission denied {operation} file: {file_path}")
        print("   Check file permissions and ownership")
    elif isinstance(e, FileNotFoundError):
        print(f"❌ File not found when {operation}: {file_path}")
        print("   Verify the file path is correct")
    elif isinstance(e, OSError) and "No space left" in str(e):
        print(f"❌ No disk space available when {operation} file: {file_path}")
    elif isinstance(e, OSError):
        print(f"❌ System error {operation} file {file_path}: {e}")
    else:
        print(f"❌ Unexpected error {operation} file {file_path}: {e}")


def log_processing_progress(current: int, total: int, item_name: str = "items") -> None:
    """
    Log processing progress with consistent formatting.

    Args:
        current: Current item number (1-based)
        total: Total number of items
        item_name: Description of what's being processed
    """
    percentage = (current / total * 100) if total > 0 else 0
    print(f"  [{current:3d}/{total}] ({percentage:5.1f}%) {item_name}")


def graceful_exit(message: str, exit_code: int = 1) -> None:
    """
    Exit gracefully with a standardized message.

    Args:
        message: Exit message to display
        exit_code: Exit code (0 for success, >0 for error)
    """
    if exit_code == 0:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    sys.exit(exit_code)


def with_error_context(operation_name: str) -> Callable:
    """
    Decorator to provide error context for functions.

    Args:
        operation_name: Name of the operation for error messages
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except DremelDocsError:
                # Re-raise our custom errors without modification
                raise
            except Exception as e:
                print(f"❌ Error in {operation_name}: {e}")
                if "--debug" in sys.argv:
                    traceback.print_exc()
                raise DremelDocsError(f"{operation_name} failed: {e}") from e

        return wrapper

    return decorator


def setup_error_handling(debug: bool = False) -> None:
    """
    Set up global error handling configuration.

    Args:
        debug: Enable debug mode with full tracebacks
    """
    if debug:
        print("🐛 Debug mode enabled - full tracebacks will be shown")

    # Set up custom exception hook for unhandled exceptions
    def custom_excepthook(
        exc_type: type, exc_value: BaseException, exc_traceback: Any
    ) -> None:
        if issubclass(exc_type, DremelDocsError):
            print(f"❌ {exc_value}")
        else:
            print(f"❌ Unexpected error: {exc_value}")
            if debug:
                if exc_traceback is not None and issubclass(exc_type, BaseException):
                    traceback.print_exception(exc_type, exc_value, exc_traceback)

    sys.excepthook = custom_excepthook


# Example usage patterns for common operations
def safe_json_load(file_path: Path) -> Optional[dict]:
    """
    Safely load JSON with standardized error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded JSON data or None if failed
    """
    import json

    try:
        validate_file_path(file_path, must_exist=True)
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return None
    except json.JSONDecodeError as e:
        handle_json_error(e, file_path)
        return None
    except Exception as e:
        handle_file_operation_error(e, "reading", file_path)
        return None


def safe_json_save(data: dict, file_path: Path) -> bool:
    """
    Safely save JSON with standardized error handling.

    Args:
        data: Data to save
        file_path: Path to save JSON file

    Returns:
        True if successful, False otherwise
    """
    import json

    try:
        validate_directory_path(file_path.parent, create_if_missing=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        handle_file_operation_error(e, "writing", file_path)
        return False


if __name__ == "__main__":
    # Test the error handling utilities
    print("🧪 Testing error handling utilities")

    # Test safe execution
    def risky_operation() -> str:
        raise ValueError("Test error")

    result = safe_execute(
        risky_operation,
        fallback="fallback_value",
        error_message="Test operation failed",
    )
    print(f"Safe execute result: {result}")

    # Test validation
    try:
        validate_file_path(Path("nonexistent.txt"))
    except ValidationError as e:
        print(f"Validation caught: {e}")

    print("✅ Error handling tests complete")
