#!/bin/bash
# Run all tests with uv

echo "🧪 Running Voron Configurator Tests"
echo "=================================="
echo ""

echo "📋 Running API tests (fast)..."
uv run pytest tests/test_api.py -v
API_EXIT=$?

echo ""
echo "🖥️  Running UI tests (requires browser)..."
uv run pytest tests/test_ui.py -v --headed
UI_EXIT=$?

echo ""
echo "=================================="
echo "✅ API Tests: $([ $API_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
echo "✅ UI Tests: $([ $UI_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"

exit $((API_EXIT + UI_EXIT))
