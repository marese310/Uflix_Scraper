from utils.browser import init_driver
from scrapers.movie_list import get_movie_links
from scrapers.movie_streams import extract_streams
import os, json, csv, sqlite3, subprocess, time, webbrowser
from datetime import datetime
from win10toast import ToastNotifier
import requests

# === CONFIG ===
API_SCRIPT = "api.py"
DASHBOARD_FILE = "dashboard.html"
TELEGRAM_ENABLED = True
TELEGRAM_TOKEN = "your-bot-token-here"
TELEGRAM_CHAT_ID = "your-chat-id-here"

notifier = ToastNotifier()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"scrape_{timestamp}.txt")

def log(msg):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def send_telegram(msg):
    if not TELEGRAM_ENABLED: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        requests.post(url, data=data)
        log("✅ Telegram alert sent.")
    except Exception as e:
        log(f"❌ Telegram failed: {e}")

start = time.time()
driver = init_driver()
json_path = "data/movies.json"
movies = []
existing_links = set()

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            movies = json.load(f)
            existing_links = {m.get("url") for m in movies if m.get("url")}
        except:
            movies = []

log("▶️ Starting scraper...")

new_count = 0
try:
    for link in get_movie_links(driver):
        if link in existing_links:
            log(f"⏭️ Skipping: {link}")
            continue

        log(f"🔍 Scraping: {link}")
        data = extract_streams(driver, link)
        if data:
            movies.append(data)
            new_count += 1
        else:
            log(f"⚠️ Failed to scrape: {link}")
finally:
    driver.quit()

# Save JSON
os.makedirs("data", exist_ok=True)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=2)
log("💾 Saved movies.json")

# Export CSV
csv_path = "data/movies.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "url", "year", "rating", "genres", "streams"])
    writer.writeheader()
    for m in movies:
        writer.writerow({
            "title": m.get("title", ""),
            "url": m.get("url", ""),
            "year": m.get("year", ""),
            "rating": m.get("rating", ""),
            "genres": ", ".join(m.get("genres", [])),
            "streams": ", ".join(m.get("streams", []))
        })
log("📄 Exported movies.csv")

# Export SQLite
conn = sqlite3.connect("data/movies.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, url TEXT UNIQUE, year INTEGER,
    rating TEXT, genres TEXT, streams TEXT
)""")

for m in movies:
    try:
        c.execute("INSERT OR IGNORE INTO movies (title, url, year, rating, genres, streams) VALUES (?, ?, ?, ?, ?, ?)", (
            m.get("title", ""), m.get("url", ""), m.get("year"),
            m.get("rating"), ", ".join(m.get("genres", [])), ", ".join(m.get("streams", []))
        ))
    except Exception as e:
        log(f"❌ DB Insert Failed: {m.get('title')} - {e}")

conn.commit()
conn.close()
log("🗃️ Saved SQLite DB")

# Runtime
duration = round(time.time() - start, 2)
summary = f"✅ UFlix: Scrape complete | {new_count} new movies | Duration: {duration}s"
log(summary)
notifier.show_toast("UFlix Scraper", summary, duration=5, threaded=True)
send_telegram(summary + "\n📊 http://localhost:8000/dashboard.html")

# Auto-launch API & dashboard
try:
    subprocess.Popen(["python", API_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    subprocess.Popen(["python", "-m", "http.server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    webbrowser.open("http://localhost:8000/dashboard.html")
    log("🌐 Dashboard launched.")
except Exception as e:
    log(f"❌ Dashboard/API launch error: {e}")
