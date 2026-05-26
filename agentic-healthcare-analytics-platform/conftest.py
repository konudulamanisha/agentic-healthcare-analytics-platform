"""
conftest.py — Pytest configuration for Agentic Healthcare Analytics Platform
Adds src/ to sys.path so all imports work from tests/
"""
import sys
import os

# Make src/ importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
