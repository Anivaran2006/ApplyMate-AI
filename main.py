"""
ApplyMate AI – Root Application Entry Point
Enables seamless deployment on Render, Railway, Vercel, and local runners.
"""
import importlib.util
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Explicitly load app from backend/main.py
backend_main_path = backend_dir / "main.py"
spec = importlib.util.spec_from_file_location("backend_main", backend_main_path)
backend_main = importlib.util.module_from_spec(spec)
sys.modules["backend_main"] = backend_main
spec.loader.exec_module(backend_main)

app = backend_main.app
