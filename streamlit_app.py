"""
PONS AUTO - Streamlit Cloud Entry Point
This file exists to help Streamlit Cloud find the app correctly.
It simply imports and runs the main dashboard app.
"""

import sys
from pathlib import Path

# Add dashboard directory to path so imports work
dashboard_dir = Path(__file__).parent / "dashboard"
sys.path.insert(0, str(dashboard_dir))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
