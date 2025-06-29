
from flask import Flask, jsonify, request
import json


    

app = Flask(__name__)
app.run(host="0.0.0.0", port=5000, debug=True)

# Load data at startup
with open("data/movies.json", "r", encoding="utf-8") as f:
    MOVIES = json.load(f)

@app.route("/")
def home():
    return jsonify({
        "message": "🎬 UFlix Movie API",
        "routes": ["/movies", "/search", "/genres", "/years"]
    })

@app.route("/movies")
def all_movies():
    return jsonify(MOVIES)

@app.route("/search")
def search_movies():
    query = request.args.get("q", "").lower()
    results = [
        m for m in MOVIES
        if query in m["title"].lower()
    ]
    return jsonify(results)

@app.route("/genres")
def list_genres():
    genres = sorted({g for m in MOVIES for g in m.get("genres", [])})
    return jsonify(genres)

@app.route("/years")
def list_years():
    years = sorted({m.get("year") for m in MOVIES if m.get("year")})
    return jsonify(years)

@app.route("/filter")
def filter_movies():
    genre = request.args.get("genre", "").lower()
    year = request.args.get("year")

    filtered = [
        m for m in MOVIES
        if (not genre or genre in [g.lower() for g in m.get("genres", [])])
        and (not year or str(m.get("year")) == str(year))
    ]
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
