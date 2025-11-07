from flask import Flask
from ai_project_manager import AIProjectManager

app = Flask(__name__)

# we create this later, inside the app context
ai_project_manager = None

@app.before_first_request
def init_ai_manager():
    global ai_project_manager
    ai_project_manager = AIProjectManager()
    with app.app_context():
        ai_project_manager.initialize_all()
        print("✅ AI Project Manager initialized inside Flask app context")

@app.route("/")
def home():
    return "DreamFrame LLC backend is running on Render!"
