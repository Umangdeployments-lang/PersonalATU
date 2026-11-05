"""
UI-01: Next.js 15 + WebGL 60-FPS Footprint/Heatmap Console
This module provides the Python-side dashboard server (Flask/FastAPI) that feeds the Next.js UI.
The actual Next.js UI lives in /src/app (TypeScript/React).
"""
from src.dashboard import app as flask_app, update_dashboard

__all__ = ["flask_app", "update_dashboard"]