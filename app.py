from flask import Flask, jsonify, render_template, request

from scraper import UNIT_LABELS, search_appointments

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/search")
def api_search():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    unit = data.get("unit") or ""
    doctor_query = data.get("doctor_query") or ""

    if not username or not password:
        return jsonify({"ok": False, "error": "Patient code and password are required."}), 400
    if unit not in UNIT_LABELS:
        return jsonify({"ok": False, "error": "Invalid unit selection."}), 400

    result = search_appointments(username, password, unit, doctor_query)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
