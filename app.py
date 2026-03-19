from flask import Flask, Response, request
from database import init_db, record_visit, get_total, get_daily_counts, get_first_visit_date
from svg_generator import build_svg

app = Flask(__name__)
init_db()

@app.route("/count/<username>")
def count(username):
    agent = request.headers.get("User-Agent", "")
    if "camo" not in agent.lower():
        record_visit(username)

    total      = get_total(username)
    daily      = get_daily_counts(username, days=7)
    first_date = get_first_visit_date(username)
    svg        = build_svg(total, daily, first_date)

    return Response(
        svg,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
            "Expires":       "0",
            "s-maxage":      "1",
        }
    )

@app.route("/api/<username>")
def api(username):
    from flask import jsonify
    from datetime import date
    total      = get_total(username)
    first_date = get_first_visit_date(username)
    today      = date.today().strftime("%b %d, %Y")
    return jsonify({
        "username"  : username,
        "total"     : total,
        "since"     : first_date,
        "today"     : today,
        "date_range": f"{first_date} -> {today}"
    })

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
