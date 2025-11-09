from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return """
    <html>
      <head>
        <title>DreamFrame LLC</title>
      </head>
      <body style="font-family: sans-serif; padding: 40px; background: #0f172a; color: #fff;">
        <h1>🚀 DreamFrame LLC is Live</h1>
        <p>This is your Flask app running on Render.</p>
        <p>You can replace this with your real frontend later.</p>
      </body>
    </html>
    """
