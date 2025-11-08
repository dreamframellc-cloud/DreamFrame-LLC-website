from flask import Flask, jsonify

from ai_project_manager import AIProjectManager


app = Flask(__name__)

# This will be populated the first time the server begins handling traffic.
ai_project_manager = None


@app.before_request
def ensure_ai_manager_initialized() -> None:
    """Lazily initialize the AI project manager inside a Flask app context."""
    global ai_project_manager

    if ai_project_manager is not None:
                        return
                    
    ai_project_manager = AIProjectManager()

    # Guard against the manager not exposing an `initialize_all` helper.
    initializer = getattr(ai_project_manager, "initialize_all", None)
    if callable(initializer):
        initializer()

    app.logger.info("✅ AI Project Manager initialized inside Flask app context")


@app.route("/")
def home() -> str:
    return "DreamFrame LLC backend is running on Render!"


@app.route("/status")
def status():
    """Return live health and AI system status."""
    status_info = {
        "status": "ok",
        "ai_manager_initialized": ai_project_manager is not None,
        "environment": "Render Cloud",
        "service": "DreamFrame LLC Backend",
    }
    return jsonify(status_info), 200
