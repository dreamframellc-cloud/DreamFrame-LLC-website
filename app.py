from flask import Flask
from ai_project_manager import AIProjectManager

app = Flask(__name__)

# we create this later, inside the app context
ai_project_manager = None

@app.before_serving
def init_ai_manager():
    """Initialize AI manager once the server is ready to serve requests."""
    global ai_project_manager
    if ai_project_manager is None:
        ai_project_manager = AIProjectManager()
with app.app_context():
            # Guard against missing initialize_all implementation
            initializer = getattr(ai_project_manager, "initialize_all", None)
            if callable(initializer):
                initializer()
            print("✅ AI Project Manager initialized inside Flask app context")

@app.route("/")
def home():
    return "DreamFrame LLC backend is running on Render!"
