from flask import Flask, render_template, request, redirect, session, url_for, jsonify, Response, send_from_directory
from flask_socketio import SocketIO
import mysql.connector
import csv
from io import StringIO
import os

app = Flask(__name__)
app.secret_key = "CHANGE_ME"

socketio = SocketIO(app)

# ================= DB CONNECTION =================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="appuser",
        password="CHANGE_ME",
        database="surveillance_db"
    )


# ================= SERVE EVIDENCE IMAGES =================
@app.route('/evidence/<filename>')
def serve_evidence(filename):
    return send_from_directory('evidence', filename)


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Demo credentials
        if username == "admin" and password == "admin":
            session["user"] = username
            return redirect(url_for("dashboard"))

        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
    logs = cursor.fetchall()

    total = len(logs)

    unauthorized = sum(
        1 for log in logs
        if log["status"] in ["MEDIUM", "HIGH", "UNAUTHORIZED"]
    )

    authorized = sum(
        1 for log in logs
        if log["status"] == "AUTHORIZED"
    )

    # ⭐ NEW: Latest Alert (Step 6)
    latest_alert = logs[0] if logs else None

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        logs=logs,
        total=total,
        unauthorized=unauthorized,
        authorized=authorized,
        latest_alert=latest_alert   # ⭐ Added
    )


# ================= REAL-TIME API =================
@app.route("/api/latest")
def latest_data():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
    logs = cursor.fetchall()

    total = len(logs)

    unauthorized = sum(
        1 for log in logs
        if log["status"] in ["MEDIUM", "HIGH", "UNAUTHORIZED"]
    )

    authorized = sum(
        1 for log in logs
        if log["status"] == "AUTHORIZED"
    )

    cursor.close()
    db.close()

    return jsonify({
        "total": total,
        "unauthorized": unauthorized,
        "authorized": authorized,
        "logs": logs
    })


# ================= EXPORT CSV =================
@app.route("/export")
def export_csv():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()

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

    writer.writerows(rows)

    output = Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment;filename=surveillance_logs.csv"
        }
    )

    cursor.close()
    db.close()

    return output


# ================= LOGOUT =================
@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("login"))


# ================= SOCKET EVENT =================
@socketio.on("connect")
def handle_connect():
    print("Client connected")


# ================= RUN =================
if __name__ == "__main__":
    socketio.run(app, debug=True)