from flask import Flask, render_template, request, redirect, session, url_for, jsonify, Response, send_from_directory
import csv
from datetime import datetime, timedelta
from functools import wraps
from io import StringIO
import os
import secrets

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# Demo mode serves sample data, so the dashboard can run on a host with no
# camera, Arduino or MySQL. Vercel sets VERCEL automatically.
DEMO_MODE = (
    os.environ.get("DEMO_MODE", "").lower() in ("1", "true", "yes")
    or bool(os.environ.get("VERCEL"))
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or (
    "public-demo-session-key" if DEMO_MODE else secrets.token_hex(32)
)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

socketio = None
if not DEMO_MODE:
    from flask_socketio import SocketIO
    socketio = SocketIO(app)


# ================= DB CONNECTION =================
def get_db_connection():
    import mysql.connector

    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DASHBOARD_DB_USER", "appuser"),
        password=os.environ["DASHBOARD_DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "surveillance_db")
    )


# ================= EVENT DATA =================
DEMO_IMAGE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240">
<rect width="320" height="240" fill="#1e1e1e"/>
<circle cx="160" cy="92" r="42" fill="#555"/>
<path d="M78 216c8-58 44-84 82-84s74 26 82 84z" fill="#555"/>
<text x="160" y="228" fill="#ff4444" font-family="Arial" font-size="18" text-anchor="middle">SAMPLE IMAGE</text>
</svg>"""


def demo_events():
    now = datetime.now().replace(microsecond=0)
    samples = [
        (4, "Unknown", "UNAUTHORIZED", 0.81),
        (19, "Authorized User", "AUTHORIZED", 0.38),
        (47, "Unknown", "UNAUTHORIZED", 0.76),
        (63, "Unknown", "UNAUTHORIZED", 0.92),
        (118, "Authorized User", "AUTHORIZED", 0.41),
        (164, "Authorized User", "AUTHORIZED", 0.35),
        (231, "Unknown", "UNAUTHORIZED", 0.69),
        (306, "Authorized User", "AUTHORIZED", 0.44),
        (412, "Unknown", "UNAUTHORIZED", 0.88),
        (540, "Authorized User", "AUTHORIZED", 0.39),
    ]
    return [
        {
            "id": len(samples) - index,
            "name": name,
            "status": status,
            "distance": distance,
            "image_path": "evidence/sample.svg" if status == "UNAUTHORIZED" else None,
            "timestamp": now - timedelta(minutes=minutes),
        }
        for index, (minutes, name, status, distance) in enumerate(samples)
    ]


def get_events():
    if DEMO_MODE:
        return demo_events()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    db.close()
    return logs


def count_events(logs):
    unauthorized = sum(
        1 for log in logs
        if log["status"] in ["MEDIUM", "HIGH", "UNAUTHORIZED"]
    )
    authorized = sum(1 for log in logs if log["status"] == "AUTHORIZED")
    return unauthorized, authorized


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ================= SERVE EVIDENCE IMAGES =================
@app.route('/evidence/<filename>')
@login_required
def serve_evidence(filename):
    if DEMO_MODE:
        return Response(DEMO_IMAGE, mimetype="image/svg+xml")
    return send_from_directory('evidence', filename)


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid Credentials", demo=DEMO_MODE)

    return render_template("login.html", demo=DEMO_MODE)


# ================= DASHBOARD =================
@app.route("/dashboard")
@login_required
def dashboard():

    logs = get_events()
    unauthorized, authorized = count_events(logs)

    return render_template(
        "dashboard.html",
        logs=logs,
        total=len(logs),
        unauthorized=unauthorized,
        authorized=authorized,
        latest_alert=logs[0] if logs else None,
        demo=DEMO_MODE
    )


# ================= REAL-TIME API =================
@app.route("/api/latest")
@login_required
def latest_data():

    logs = get_events()
    unauthorized, authorized = count_events(logs)

    return jsonify({
        "total": len(logs),
        "unauthorized": unauthorized,
        "authorized": authorized,
        "logs": logs
    })


# ================= EXPORT CSV =================
@app.route("/export")
@login_required
def export_csv():

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow([
        "ID",
        "Name",
        "Status",
        "Distance",
        "Image",
        "Timestamp"
    ])

    writer.writerows(
        [log["id"], log["name"], log["status"], log["distance"], log["image_path"], log["timestamp"]]
        for log in get_events()
    )

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment;filename=surveillance_logs.csv"
        }
    )


# ================= LOGOUT =================
@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("login"))


# ================= SOCKET EVENT =================
if socketio:
    @socketio.on("connect")
    def handle_connect():
        print("Client connected")


# ================= RUN =================
if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    if socketio:
        socketio.run(app, debug=debug)
    else:
        app.run(debug=debug)
