import sqlite3, os, time
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hackathon_secret"

UPLOAD_FOLDER = "static/uploads"
VOICE_FOLDER = "static/uploads/voice"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOICE_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["VOICE_FOLDER"] = VOICE_FOLDER

# -----------------------
# DB INIT
# -----------------------
def init_db():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        area TEXT,
        complaint TEXT,
        category TEXT,
        sentiment TEXT,
        urgency TEXT,
        status TEXT,
        language TEXT,
        emotion TEXT,
        department TEXT,
        assigned_officer TEXT,
        photo TEXT,
        voice TEXT,
        lat REAL,
        lng REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------
# HOME (TEXT)
# -----------------------
@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        area = request.form.get("area")
        text = request.form.get("text")
        lat = request.form.get("lat")
        lng = request.form.get("lng")

        conn = sqlite3.connect("complaints.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO complaints(name, area, complaint, category, sentiment, urgency, status, language, emotion, department, assigned_officer, lat, lng)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (name, area, text, "General", "Neutral 😐", "Normal", "Received", "en", "Neutral", "General", "AutoAssign", lat, lng))

        conn.commit()
        conn.close()

        return render_template("index.html", result=True, category="General", sentiment="Neutral 😐")

    return render_template("index.html")

# -----------------------
# VOICE
# -----------------------
@app.route("/voice", methods=["POST"])
def voice():
    name = request.form.get("name")
    area = request.form.get("area")
    lat = request.form.get("lat")
    lng = request.form.get("lng")

    audio = request.files.get("audio")
    filename = None

    if audio and audio.filename:
        filename = str(int(time.time())) + "_" + secure_filename(audio.filename)
        audio.save(os.path.join(app.config["VOICE_FOLDER"], filename))

    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints(name, area, complaint, category, sentiment, urgency, status, language, emotion, department, assigned_officer, voice, lat, lng)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (name, area, "[Voice Complaint]", "General", "Neutral 😐", "Normal", "Received", "en", "Neutral", "General", "AutoAssign", filename, lat, lng))

    conn.commit()
    conn.close()

    return render_template("index.html", result=True, category="General", sentiment="Neutral 😐")

# -----------------------
# PHOTO
# -----------------------
@app.route("/photo", methods=["POST"])
def photo():
    name = request.form.get("name")
    area = request.form.get("area")
    lat = request.form.get("lat")
    lng = request.form.get("lng")

    photo = request.files.get("photo")
    filename = None

    if photo and photo.filename:
        filename = str(int(time.time())) + "_" + secure_filename(photo.filename)
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints(name, area, complaint, category, sentiment, urgency, status, language, emotion, department, assigned_officer, photo, lat, lng)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (name, area, "[Photo Complaint]", "General", "Neutral 😐", "Normal", "Received", "en", "Neutral", "General", "AutoAssign", filename, lat, lng))

    conn.commit()
    conn.close()

    return render_template("index.html", result=True, category="General", sentiment="Neutral 😐")

# -----------------------
# DASHBOARD (Citizen)
# -----------------------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT area, COUNT(*) FROM complaints GROUP BY area")
    area_data = cursor.fetchall()

    cursor.execute("SELECT category, COUNT(*) FROM complaints GROUP BY category")
    category_data = cursor.fetchall()

    cursor.execute("SELECT sentiment, COUNT(*) FROM complaints GROUP BY sentiment")
    sentiment_data = cursor.fetchall()

    cursor.execute("SELECT urgency, COUNT(*) FROM complaints GROUP BY urgency")
    urgency_data = cursor.fetchall()

    cursor.execute("SELECT emotion, COUNT(*) FROM complaints GROUP BY emotion")
    emotion_summary = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html",
        total=total,
        area_data=area_data,
        category_data=category_data,
        sentiment_data=sentiment_data,
        urgency_data=urgency_data,
        emotion_summary=emotion_summary
    )

# -----------------------
# OFFICER DASHBOARD
# -----------------------
@app.route("/officer", methods=["GET","POST"])
def officer_dashboard():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    if request.method == "POST":
        cid = request.form.get("id")
        status = request.form.get("status")
        cursor.execute("UPDATE complaints SET status=? WHERE id=?", (status, cid))
        conn.commit()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    cursor.execute("SELECT emotion, COUNT(*) FROM complaints GROUP BY emotion")
    emotion_summary = cursor.fetchall()

    conn.close()

    return render_template("officer.html", complaints=complaints, emotion_summary=emotion_summary)

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
