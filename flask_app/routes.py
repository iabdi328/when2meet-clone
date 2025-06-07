from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
from utils.database.database import get_db
from datetime import datetime, timedelta
from collections import defaultdict
from utils.socketio_instance import socketio  

main_routes = Blueprint("main_routes", __name__)

# ------------------ Helpers ------------------ #
def get_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    if start > end:
        start, end = end, start
    delta = end - start
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]

def get_time_slots(start_time, end_time):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    if start > end:
        start, end = end, start
    slots = []
    current = start
    while current <= end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    return slots

# ------------------ Home ------------------ #
@main_routes.route("/")
def home():
    return render_template("shared/home.html")

# ------------------ Login ------------------ #
@main_routes.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
        if user:
            session["email"] = user["email"]
            return redirect(url_for("main_routes.home"))
        return "Invalid credentials"
    return render_template("shared/login.html")

# ------------------ Register ------------------ #
@main_routes.route("/register", methods=["GET", "POST"])
def register():
    db = get_db()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        db.commit()
        return redirect(url_for("main_routes.login"))
    return render_template("shared/register.html")

# ------------------ Logout ------------------ #
@main_routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main_routes.home"))

# ------------------ Create Event ------------------ #
@main_routes.route("/create-event", methods=["GET", "POST"])
def create_event():
    if "email" not in session:
        return redirect(url_for("main_routes.login"))

    db = get_db()
    if request.method == "POST":
        title = request.form.get("title")
        specific_dates_raw = request.form.get("specific_dates")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        invitees_raw = request.form.get("invitees")

        specific_dates = [d.strip() for d in specific_dates_raw.split(",") if d.strip()]
        if not specific_dates:
            return "Please select at least one date", 400
        start_date = min(specific_dates)
        end_date = max(specific_dates)

        creator = db.execute("SELECT id FROM users WHERE email = ?", (session['email'],)).fetchone()
        if not creator:
            return "Creator not found", 400

        creator_id = creator["id"]
        db.execute("""
            INSERT INTO events (title, start_date, end_date, start_time, end_time, creator_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, start_date, end_date, start_time, end_time, creator_id))
        event_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        invitees = [email.strip() for email in invitees_raw.split(",") if email.strip()]
        for email in invitees:
            user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            user_id = user["id"] if user else None
            db.execute("INSERT INTO invites (event_id, user_id, email) VALUES (?, ?, ?)", (event_id, user_id, email))

        db.commit()
        return redirect(url_for("main_routes.availability", event_id=event_id))

    return render_template("shared/event_create.html")

# ------------------ My Events ------------------ #
@main_routes.route("/my-events")
def my_events():
    if "email" not in session:
        return redirect(url_for("main_routes.login"))

    db = get_db()
    user = db.execute("SELECT id FROM users WHERE email = ?", (session["email"],)).fetchone()
    if not user:
        return "User not found", 403

    created_events = db.execute("SELECT * FROM events WHERE creator_id = ?", (user["id"],)).fetchall()
    invited_events = db.execute("""
        SELECT DISTINCT e.* FROM events e
        JOIN invites i ON e.id = i.event_id
        WHERE i.user_id = ? OR i.email = ?
    """, (user["id"], session["email"])).fetchall()

    return render_template("shared/my_events.html", created=created_events, invited=invited_events)

# ------------------ Availability Page ------------------ #
@main_routes.route("/availability/<int:event_id>")
def availability(event_id):
    if "email" not in session:
        return redirect(url_for("main_routes.login"))

    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not event:
        return "Event not found", 404

    user = db.execute("SELECT id FROM users WHERE email = ?", (session['email'],)).fetchone()
    if not user:
        return "User not found", 403

    invited = db.execute("""
        SELECT * FROM invites 
        WHERE event_id = ? AND (user_id = ? OR email = ?)
    """, (event_id, user["id"], session["email"])).fetchone()

    if not invited and event["creator_id"] != user["id"]:
        return "Access Denied", 403

    date_range = get_date_range(event["start_date"], event["end_date"])
    time_slots = get_time_slots(event["start_time"], event["end_time"])

    availabilities = db.execute("""
        SELECT date, time, status FROM availabilities 
        WHERE user_id = ? AND event_id = ?
    """, (user["id"], event_id)).fetchall()

    availability_map = {
        f"{row['date']}|{row['time']}": row['status'] for row in availabilities
    }

    heatmap_data = db.execute("""
        SELECT date, time, status, COUNT(*) as count
        FROM availabilities
        WHERE event_id = ?
        GROUP BY date, time, status
    """, (event_id,)).fetchall()

    heatmap_map = defaultdict(lambda: {"available": 0, "maybe": 0, "unavailable": 0})
    for row in heatmap_data:
        key = f"{row['date']}|{row['time']}"
        heatmap_map[key][row['status']] = row['count']

    # Best Time Calculation
    best_slot = None
    best_score = (-1, float('inf'))
    for key, counts in heatmap_map.items():
        score = (counts.get("available", 0), -counts.get("unavailable", 0))
        if best_slot is None or score > best_score or (score == best_score and key < best_slot):
            best_slot = key
            best_score = score

    best_time_data = None
    if best_slot:
        best_time_data = {
            "date": best_slot.split("|")[0],
            "start": best_slot.split("|")[1],
            "end": (datetime.strptime(best_slot.split("|")[1], "%H:%M") + timedelta(minutes=30)).strftime("%H:%M"),
            "available": heatmap_map[best_slot]["available"]
        }

    return render_template(
        "shared/availability.html",
        event=event,
        date_range=date_range,
        time_slots=time_slots,
        availability_map=availability_map,
        heatmap_map=dict(heatmap_map),
        best_time=best_time_data
    )

# ------------------ Save Availability (with Live Sync) ------------------ #
@main_routes.route("/save-availability", methods=["POST"])
def save_availability():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    data = request.get_json()
    event_id = data.get("event_id")
    date = data.get("date")
    time = data.get("time")
    status = data.get("status")

    user = db.execute("SELECT id FROM users WHERE email = ?", (session["email"],)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 403

    user_id = user["id"]
    db.execute("""
        INSERT INTO availabilities (user_id, event_id, date, time, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, event_id, date, time)
        DO UPDATE SET status=excluded.status
    """, (user_id, event_id, date, time, status))
    db.commit()

    # Recalculate heatmap
    heatmap_data = db.execute("""
        SELECT date, time, status, COUNT(*) as count
        FROM availabilities
        WHERE event_id = ?
        GROUP BY date, time, status
    """, (event_id,)).fetchall()

    heatmap_map = defaultdict(lambda: {"available": 0, "maybe": 0, "unavailable": 0})
    for row in heatmap_data:
        key = f"{row['date']}|{row['time']}"
        heatmap_map[key][row['status']] = row['count']

    # Best time again
    best_slot = None
    best_score = (-1, float('inf'))
    for key, counts in heatmap_map.items():
        score = (counts.get("available", 0), -counts.get("unavailable", 0))
        if best_slot is None or score > best_score or (score == best_score and key < best_slot):
            best_slot = key
            best_score = score

    best_time = None
    if best_slot:
        best_time = {
            "date": best_slot.split("|")[0],
            "start": best_slot.split("|")[1],
            "end": (datetime.strptime(best_slot.split("|")[1], "%H:%M") + timedelta(minutes=30)).strftime("%H:%M"),
            "available": heatmap_map[best_slot]["available"]
        }

    # Emit real-time update to event room
    socketio.emit("availability_updated", {
        "event_id": event_id,
        "date": date,
        "time": time,
        "status": status,
        "heatmap": dict(heatmap_map),
        "best_time": best_time
    }, room=f"event_{event_id}")

    return jsonify({"success": True})
