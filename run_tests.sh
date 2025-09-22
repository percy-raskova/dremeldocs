#!/usr/bin/env bash

# Test runner script for astradocs
# Usage: ./run_tests.sh [option]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 AstraDocs Test Runner${NC}"
echo "========================="
echo ""

# Function to run tests with pretty output
run_test() {
    local name=$1
    local command=$2
    echo -e "${YELLOW}Running: $name${NC}"
    echo "Command: $command"
    echo "---------"
    eval $command
    echo ""
}

# Parse command line arguments
case "${1:-all}" in
    all)
        echo -e "${GREEN}Running all tests with coverage...${NC}\n"
        run_test "All Tests with Coverage" "pytest --cov=scripts --cov=src --cov-report=term-missing --cov-report=html"
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/${NC}"
        ;;

    unit)
        echo -e "${GREEN}Running unit tests only...${NC}\n"
        run_test "Unit Tests" "pytest tests/unit -v"
        ;;

    integration)
        echo -e "${GREEN}Running integration tests only...${NC}\n"
        run_test "Integration Tests" "pytest tests/integration -v -m integration"
        ;;

    fast)
        echo -e "${GREEN}Running fast tests (excluding slow)...${NC}\n"
        run_test "Fast Tests" "pytest -m 'not slow' -v"
        ;;

    performance)
        echo -e "${GREEN}Running performance tests...${NC}\n"
        run_test "Performance Tests" "pytest -m performance -v"
        ;;

    lint)
        echo -e "${GREEN}Running linting and type checking...${NC}\n"
        run_test "Black Format Check" "black --check scripts/ tests/ 2>/dev/null || echo 'Format issues found - run: black scripts/ tests/'"
        run_test "Ruff Linting" "ruff check scripts/ tests/ 2>/dev/null || echo 'Linting issues found'"
        run_test "MyPy Type Check" "mypy scripts/ --ignore-missing-imports 2>/dev/null || echo 'Type issues found'"
        ;;

    coverage)
        echo -e "${GREEN}Generating detailed coverage report...${NC}\n"
        run_test "Coverage Report" "pytest --cov=scripts --cov=src --cov-report=html --cov-report=term"
        echo -e "${GREEN}Opening coverage report...${NC}"
        if command -v xdg-open &> /dev/null; then
            xdg-open htmlcov/index.html
        elif command -v open &> /dev/null; then
            open htmlcov/index.html
        else
            echo "Coverage report available at: htmlcov/index.html"
        fi
        ;;

    watch)
        echo -e "${GREEN}Starting test watcher...${NC}\n"
        echo "Tests will re-run on file changes (Ctrl+C to stop)"
        if command -v pytest-watch &> /dev/null; then
            pytest-watch -- -x -v
        else
            echo -e "${RED}pytest-watch not installed. Install with: pip install pytest-watch${NC}"
            exit 1
        fi
        ;;

    specific)
        if [ -z "$2" ]; then
            echo -e "${RED}Please specify a test path${NC}"
            echo "Example: ./run_tests.sh specific tests/unit/test_local_filter_pipeline.py"
            exit 1
        fi
        echo -e "${GREEN}Running specific test: $2${NC}\n"
        run_test "Specific Test" "pytest $2 -v"
        ;;

    clean)
        echo -e "${GREEN}Cleaning test artifacts...${NC}\n"
        rm -rf .pytest_cache/
        rm -rf htmlcov/
        rm -rf .coverage
        rm -rf tests/__pycache__
        rm -rf tests/*/__pycache__
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        echo -e "${GREEN}✅ Test artifacts cleaned${NC}"
        ;;

    install)
        echo -e "${GREEN}Installing test dependencies...${NC}\n"
        pip install -r requirements-dev.txt
        echo -e "${GREEN}✅ Test dependencies installed${NC}"
        ;;

    help|--help|-h)
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all         - Run all tests with coverage (default)"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  fast        - Run fast tests (exclude slow tests)"
        echo "  performance - Run performance tests"
        echo "  lint        - Run linting and type checking"
        echo "  coverage    - Generate and open coverage report"
        echo "  watch       - Watch files and re-run tests on changes"
        echo "  specific    - Run specific test file"
        echo "  clean       - Clean test artifacts"
        echo "  install     - Install test dependencies"
        echo "  help        - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh              # Run all tests"
        echo "  ./run_tests.sh unit         # Run unit tests only"
        echo "  ./run_tests.sh specific tests/unit/test_theme_classifier.py"
        ;;

    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Tests completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Tests failed!${NC}"
    exit 1
fi