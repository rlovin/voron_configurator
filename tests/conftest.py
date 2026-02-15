"""Test configuration for Voron Configurator"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from flask import Flask
from app import app as flask_app


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config.update({
        'TESTING': True,
        'SERVER_NAME': 'localhost:3000'
    })
    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for Playwright tests."""
    return "http://localhost:3000"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Browser context arguments - start minimized."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Browser launch arguments - start minimized behind terminal."""
    return {
        "args": ["--window-position=10000,10000"],  # Position off-screen to keep behind
        "headless": False,
    }


@pytest.fixture(scope="class")
def live_server():
    """Start Flask server for testing (used by syntax tests)."""
    import subprocess
    import time
    import signal
    
    # Start server
    proc = subprocess.Popen(
        ["uv", "run", "python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    class Server:
        url = "http://localhost:3000"
    
    yield Server()
    
    # Cleanup
    proc.send_signal(signal.SIGTERM)
    proc.wait()
