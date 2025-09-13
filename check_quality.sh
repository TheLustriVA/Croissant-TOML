#!/bin/bash

# Local Quality Checks and Auto-fixes for Croissant-TOML
# This script runs all the same checks as the CI pipeline locally
# so you can fix issues before pushing to GitHub

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
RUN_TESTS=true
RUN_SECURITY=true
RUN_TYPE_CHECK=true
AUTO_FIX=true
VERBOSE=false

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section headers
print_section() {
    echo
    echo "=================================="
    print_status $BLUE "$1"
    echo "=================================="
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install missing dependencies
install_deps() {
    print_section "🔧 Checking Dependencies"

    local missing_deps=()

    if ! command_exists black; then missing_deps+=("black"); fi
    if ! command_exists isort; then missing_deps+=("isort"); fi
    if ! command_exists flake8; then missing_deps+=("flake8"); fi
    if ! command_exists mypy; then missing_deps+=("mypy"); fi
    if ! command_exists bandit; then missing_deps+=("bandit"); fi
    if ! command_exists safety; then missing_deps+=("safety"); fi
    if ! command_exists pytest; then missing_deps+=("pytest"); fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_status $YELLOW "Missing dependencies: ${missing_deps[*]}"
        print_status $YELLOW "Installing with UV..."
        uv pip install "${missing_deps[@]}"
    else
        print_status $GREEN "✅ All dependencies available"
    fi
}

# Function to run auto-fixers
run_auto_fixers() {
    if [ "$AUTO_FIX" = true ]; then
        print_section "🔧 Auto-fixing Code Style"

        # Black - code formatting
        print_status $BLUE "Running Black (code formatter)..."
        if black croissant_toml/ tests/ --line-length 88; then
            print_status $GREEN "✅ Black formatting applied"
        else
            print_status $RED "❌ Black failed"
            return 1
        fi

        # isort - import sorting
        print_status $BLUE "Running isort (import sorter)..."
        if isort croissant_toml/ tests/ --profile black; then
            print_status $GREEN "✅ Import sorting applied"
        else
            print_status $RED "❌ isort failed"
            return 1
        fi

        print_status $GREEN "🎉 Auto-fixes completed!"
    fi
}

# Function to run linting checks
run_linting() {
    print_section "🔍 Code Quality Checks"

    local lint_failed=false

    # Flake8 - linting
    print_status $BLUE "Running Flake8 (linter)..."
    if flake8 croissant_toml/ tests/ --max-line-length=88 --extend-ignore=E203; then
        print_status $GREEN "✅ Flake8 passed"
    else
        print_status $RED "❌ Flake8 found issues"
        lint_failed=true
    fi

    # Check if auto-fix helped
    if [ "$lint_failed" = true ] && [ "$AUTO_FIX" = true ]; then
        print_status $YELLOW "💡 Try running the auto-fixers first:"
        print_status $YELLOW "   black croissant_toml/ tests/"
        print_status $YELLOW "   isort croissant_toml/ tests/ --profile black"
    fi

    return $([ "$lint_failed" = false ])
}

# Function to run type checking
run_type_checking() {
    if [ "$RUN_TYPE_CHECK" = true ]; then
        print_section "🔍 Type Checking"

        print_status $BLUE "Running MyPy (type checker)..."
        if mypy croissant_toml/ --ignore-missing-imports; then
            print_status $GREEN "✅ Type checking passed"
        else
            print_status $RED "❌ Type checking failed"
            print_status $YELLOW "💡 Fix type hints in the failing files"
            return 1
        fi
    fi
}

# Function to run security checks
run_security_checks() {
    if [ "$RUN_SECURITY" = true ]; then
        print_section "🛡️  Security Checks"

        # Bandit - security linter
        print_status $BLUE "Running Bandit (security scanner)..."
        if bandit -r croissant_toml/ -x tests/; then
            print_status $GREEN "✅ Security scan passed"
        else
            print_status $RED "❌ Security issues found"
            return 1
        fi

        # Safety - dependency vulnerability check
        print_status $BLUE "Running Safety (dependency scanner)..."
        if safety check --json > /dev/null 2>&1; then
            print_status $GREEN "✅ Dependency security check passed"
        else
            print_status $YELLOW "⚠️  Some dependency vulnerabilities found (check with: safety check)"
            # Don't fail the script for this as it might be false positives
        fi
    fi
}

# Function to run tests
run_tests() {
    if [ "$RUN_TESTS" = true ]; then
        print_section "🧪 Running Tests"

        print_status $BLUE "Running pytest with coverage..."
        if [ -d "tests" ]; then
            if pytest tests/ --cov=croissant_toml --cov-report=term-missing; then
                print_status $GREEN "✅ All tests passed"
            else
                print_status $RED "❌ Some tests failed"
                return 1
            fi
        else
            print_status $YELLOW "⚠️  No tests directory found"
            print_status $YELLOW "   Create tests/ directory and add test files"
        fi
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_section "🔄 Integration Tests"

    print_status $BLUE "Testing CLI conversions..."

    # Check if sample.json exists
    if [ ! -f "sample.json" ]; then
        print_status $YELLOW "⚠️  sample.json not found, skipping integration tests"
        return 0
    fi

    # Test conversion workflow
    if python -m croissant_toml.cli to-toml sample.json -o test_output.toml 2>/dev/null; then
        print_status $GREEN "✅ JSON-LD to TOML conversion worked"
    else
        print_status $RED "❌ JSON-LD to TOML conversion failed"
        return 1
    fi

    if python -m croissant_toml.cli validate test_output.toml 2>/dev/null; then
        print_status $GREEN "✅ TOML validation passed"
    else
        print_status $RED "❌ TOML validation failed"
        return 1
    fi

    if python -m croissant_toml.cli to-json test_output.toml -o roundtrip.json 2>/dev/null; then
        print_status $GREEN "✅ TOML to JSON-LD conversion worked"
    else
        print_status $RED "❌ TOML to JSON-LD conversion failed"
        return 1
    fi

    # Clean up test files
    rm -f test_output.toml roundtrip.json
    print_status $GREEN "🎉 Integration tests passed!"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Local quality checks and auto-fixes for Croissant-TOML"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  --no-fix            Skip auto-fixes (Black, isort)"
    echo "  --no-tests          Skip running tests"
    echo "  --no-security       Skip security checks"
    echo "  --no-types          Skip type checking"
    echo "  --lint-only         Run only linting (no tests, security, or types)"
    echo "  --fix-only          Run only auto-fixers"
    echo "  --integration       Run integration tests"
    echo "  -v, --verbose       Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                  Run all checks with auto-fixes"
    echo "  $0 --fix-only       Only run Black and isort"
    echo "  $0 --lint-only      Only run Flake8"
    echo "  $0 --no-fix         Run all checks without auto-fixes"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --no-fix)
            AUTO_FIX=false
            shift
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --no-security)
            RUN_SECURITY=false
            shift
            ;;
        --no-types)
            RUN_TYPE_CHECK=false
            shift
            ;;
        --lint-only)
            RUN_TESTS=false
            RUN_SECURITY=false
            RUN_TYPE_CHECK=false
            AUTO_FIX=false
            shift
            ;;
        --fix-only)
            RUN_TESTS=false
            RUN_SECURITY=false
            RUN_TYPE_CHECK=false
            shift
            ;;
        --integration)
            RUN_TESTS=false
            RUN_SECURITY=false
            RUN_TYPE_CHECK=false
            AUTO_FIX=false
            INTEGRATION_ONLY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_section "🚀 Croissant-TOML Local Quality Checks"

    # Install missing dependencies
    install_deps

    # Track overall success
    local overall_success=true

    # Run integration tests only if requested
    if [ "${INTEGRATION_ONLY:-false}" = true ]; then
        run_integration_tests || overall_success=false
    else
        # Run auto-fixers first
        run_auto_fixers || overall_success=false

        # Run linting
        run_linting || overall_success=false

        # Run type checking
        run_type_checking || overall_success=false

        # Run security checks
        run_security_checks || overall_success=false

        # Run tests
        run_tests || overall_success=false
    fi

    # Final summary
    echo
    echo "=================================="
    if [ "$overall_success" = true ]; then
        print_status $GREEN "🎉 ALL CHECKS PASSED!"
        print_status $GREEN "✅ Ready to commit and push to GitHub"
    else
        print_status $RED "❌ SOME CHECKS FAILED"
        print_status $YELLOW "💡 Fix the issues above before committing"
        exit 1
    fi
    echo "=================================="
}

# Run main function
main
