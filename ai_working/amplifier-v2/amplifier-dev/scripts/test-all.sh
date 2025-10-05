#!/bin/bash
# Test runner for all Amplifier modules

set -e

echo "Running Amplifier test suite..."
echo "=============================="

# Track test results
FAILED_MODULES=()
PASSED_MODULES=()

# Test core
echo -e "\n[TEST] amplifier-core"
if (cd amplifier-core && python -m pytest tests/ -v 2>&1); then
    PASSED_MODULES+=("amplifier-core")
    echo "✅ amplifier-core tests passed"
else
    FAILED_MODULES+=("amplifier-core")
    echo "❌ amplifier-core tests failed"
fi

# Test each module
for module in amplifier-mod-*/; do
    if [ -d "$module" ]; then
        module_name=$(basename "$module")
        echo -e "\n[TEST] $module_name"
        
        # Check if tests directory exists
        if [ -d "${module}tests" ]; then
            if (cd "$module" && python -m pytest tests/ -v 2>&1); then
                PASSED_MODULES+=("$module_name")
                echo "✅ $module_name tests passed"
            else
                FAILED_MODULES+=("$module_name")
                echo "❌ $module_name tests failed"
            fi
        else
            echo "⚠️  $module_name has no tests"
        fi
    fi
done

# Summary
echo -e "\n=============================="
echo "Test Summary:"
echo "Passed: ${#PASSED_MODULES[@]} modules"
echo "Failed: ${#FAILED_MODULES[@]} modules"

if [ ${#FAILED_MODULES[@]} -gt 0 ]; then
    echo -e "\nFailed modules:"
    for module in "${FAILED_MODULES[@]}"; do
        echo "  - $module"
    done
    exit 1
else
    echo -e "\n✅ All tests passed!"
fi
