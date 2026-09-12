"""
Mental Health Score Predictor - Streamlit Entrypoint
"""
from pathlib import Path

# Execute streamlit_app.py directly
app_file = Path(__file__).resolve().parent / "streamlit_app.py"
with open(app_file, encoding="utf-8") as f:
    exec(f.read())
