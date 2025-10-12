#!/bin/bash

# Script to run backend tests
# Usage: ./run_tests.sh [options]

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  X Automation Backend Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing test dependencies...${NC}"
    uv add httpx pytest pytest-asyncio pytest-cov pytest-mock python-dotenv
fi

# Parse command line arguments
case "${1:-all}" in
    help)
        echo -e "${GREEN}Usage: ./run_tests.sh [option]${NC}"
        echo ""
        echo "Options:"
        echo "  help        - Show this help message"
        echo "  all         - Run all tests (default)"
        echo "  coverage    - Run tests with coverage report"
        echo "  api         - Run API endpoint tests only"
        echo "  utils       - Run utility function tests only"
        echo "  state       - Run state management tests only"
        echo "  graph       - Run graph logic tests only"
        echo "  integration - Run integration tests only"
        echo "  fast        - Run fast tests (skip integration)"
        echo "  watch       - Run tests in watch mode"
        exit 0
        ;;
    all)
        echo -e "${GREEN}Running all tests...${NC}\n"
        pytest -v
        ;;
    
    coverage)
        echo -e "${GREEN}Running tests with coverage...${NC}\n"
        pytest --cov=app --cov-report=html --cov-report=term
        echo -e "\n${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    api)
        echo -e "${GREEN}Running API tests...${NC}\n"
        pytest -v tests/test_api/
        ;;
    
    utils)
        echo -e "${GREEN}Running utility tests...${NC}\n"
        pytest -v tests/test_utils/
        ;;
    
    state)
        echo -e "${GREEN}Running state management tests...${NC}\n"
        pytest -v tests/test_state/
        ;;
    
    graph)
        echo -e "${GREEN}Running graph logic tests...${NC}\n"
        pytest -v tests/test_graph/
        ;;
    
    integration)
        echo -e "${GREEN}Running integration tests...${NC}\n"
        pytest -v -m integration tests/test_integration/
        ;;
    
    fast)
        echo -e "${GREEN}Running fast tests (excluding integration)...${NC}\n"
        pytest -v -m "not integration"
        ;;
    
    watch)
        echo -e "${GREEN}Running tests in watch mode...${NC}\n"
        pytest-watch -v
        ;;
    
    *)
        echo -e "${YELLOW}Unknown option: $1${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  help        - Show this help message"
        echo "  all         - Run all tests (default)"
        echo "  coverage    - Run tests with coverage report"
        echo "  api         - Run API endpoint tests only"
        echo "  utils       - Run utility function tests only"
        echo "  state       - Run state management tests only"
        echo "  graph       - Run graph logic tests only"
        echo "  integration - Run integration tests only"
        echo "  fast        - Run fast tests (skip integration)"
        echo "  watch       - Run tests in watch mode"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✓ Test run complete!${NC}"

