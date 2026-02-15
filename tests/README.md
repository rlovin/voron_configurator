# Testing Voron Configurator

This project uses **pytest** with **Playwright** for comprehensive testing.

## Installation (using uv)

```bash
# Install test dependencies
uv pip install pytest pytest-playwright

# Install Playwright browsers (only chromium needed)
uv run playwright install chromium
```

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run only API tests (fast)
```bash
uv run pytest tests/test_api.py -v
```

### Run only UI tests (requires browser)
```bash
uv run pytest tests/test_ui.py -v
```

### Run in headless mode (CI/CD)
```bash
uv run pytest --headless
```

### Run with headed mode (you can see the browser)
```bash
uv run pytest --headed
```

### Run specific test
```bash
uv run pytest tests/test_ui.py::TestConfigGeneration::test_generate_config_updates_editor -v
```

### Run with slow motion (to see what's happening)
```bash
uv run pytest --slowmo 1000
```

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_api.py          # Backend API tests (fast, no browser)
└── test_ui.py           # Frontend UI tests with Playwright (slower)
```

## Test Coverage

### API Tests (`test_api.py`)
- ✅ Config generation for different printers/boards
- ✅ Leviathan STM32F446 verification
- ✅ LDO reference config endpoints
- ✅ Error handling for missing fields

### UI Tests (`test_ui.py`)
- ✅ Page loads correctly
- ✅ Editor visible and functional
- ✅ Config generation updates editor
- ✅ Reference config loading (main tab and new tabs)
- ✅ Theme switching
- ✅ Info panel updates
- ✅ Download button states

## Writing New Tests

### API Test Example
```python
def test_something(client):
    response = client.post('/api/generate', json={...})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
```

### UI Test Example
```python
def test_something(page: Page, live_server):
    page.goto(live_server.url)
    page.click("#button")
    expect(page.locator("#result")).to_contain_text("Success")
```

## Debugging Failed Tests

### Screenshot on failure
```bash
uv run pytest --screenshot only-on-failure
```

### Full trace (step-by-step)
```bash
uv run pytest --tracing on
# Then view with: uv run playwright show-trace test-results/trace.zip
```

### Interactive debugger
```bash
# Run a specific test with PDB
uv run pytest tests/test_ui.py::TestClass::test_method --pdb
```

## CI/CD Configuration

For GitHub Actions:
```yaml
- name: Run tests
  run: |
    uv pip install pytest pytest-playwright
    uv run playwright install chromium
    uv run pytest --headless
```

## Troubleshooting

### Browser won't start
```bash
# Reinstall browsers
uv run playwright install --force
```

### Tests timeout
```bash
# Increase timeouts
uv run pytest --timeout 60
```

### Port already in use
```bash
# Find and kill process on port 3000
lsof -i :3000
kill -9 <PID>
```

## Test Configuration

Edit `pytest.ini` to change:
- Headless vs headed mode
- Browser choice (chromium/firefox/webkit)
- Slow motion timing
- Test markers and filtering
