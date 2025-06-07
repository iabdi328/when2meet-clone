from flask import Flask
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask_socketio import join_room, leave_room

from routes import main_routes
from utils.database.database import get_db, close_db
from utils.socketio_instance import socketio  

# ------------------ Flask App Setup ------------------ #
app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
CORS(app)
socketio.init_app(app, cors_allowed_origins="*")  

# ------------------ Register Blueprints ------------------ #
app.register_blueprint(main_routes)

# ------------------ Teardown DB ------------------ #
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

# ------------------ Custom Jinja2 Filter ------------------ #
@app.template_filter("datetimeformat")
def datetimeformat(value, format="%B %d, %Y"):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime(format)
    except Exception:
        return value  # fallback if parsing fails

# ------------------ Socket.IO Events ------------------ #
@socketio.on("join_event")
def handle_join_event(data):
    event_id = data.get("event_id")
    if event_id:
        join_room(f"event_{event_id}")

@socketio.on("leave_event")
def handle_leave_event(data):
    event_id = data.get("event_id")
    if event_id:
        leave_room(f"event_{event_id}")

# ------------------ Run Server ------------------ #
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
