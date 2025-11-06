"""
Vercel serverless function - Flask app entry point
"""

import os
import sys
import traceback

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Try to import with error handling
try:
    from app import app
    print("✅ Flask app imported successfully")
except Exception as e:
    error_msg = f"❌ Error importing Flask app: {str(e)}\n"
    error_msg += traceback.format_exc()
    print(error_msg, file=sys.stderr)
    
    # Create a minimal error app for debugging
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"""
        <h1>Import Error</h1>
        <p>Error: {str(e)}</p>
        <pre>{traceback.format_exc()}</pre>
        """, 500

