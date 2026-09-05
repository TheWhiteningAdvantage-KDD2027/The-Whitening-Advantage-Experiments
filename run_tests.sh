#!/usr/bin/env bash
set -e
echo "Running validation tests..."
pytest tests/
echo "Tests Passed."