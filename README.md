🔧 Movie scraper and dashboard launcher for uflix.cc — built with Python, tkinter, and serious hustle. > 📈 Local dashboard, daily scraping, JSON logging, process control, and system tray integration.

✨ Features
🕵️‍♂️ Web Scraper: Extracts movie data and exports to .json, .csv, and SQLite

🧭 Dashboard Launcher: Opens a local HTML dashboard and API endpoint

🧠 Password-Protected GUI: Prevent unauthorized access to scraper functions

📦 ZIP Packager: One-click export of your entire project for sharing or archiving

🖼️ Live Chart Panel: Visualizes scrape history using matplotlib

🧲 Minimize to Tray: System tray integration with pystray

⏰ Daily Scheduler: Automate scraping at your preferred time

🪪 Native Notifications: Windows popups without deprecated packages

🛠 Tech Stack
Component	Description
Python 3.10+	Core language
tkinter	GUI framework
pystray	System tray integration
matplotlib	Scrape trends chart
schedule	Background automation scheduler
sqlite3	Export format (via main.py)
subprocess + psutil	Process management
🚀 Getting Started
Clone the repo

bash
git clone https://github.com/marese310/Uflix_Scraper.git
cd Uflix_Scraper
Install requirements (Optional: create virtual environment)

bash
pip install -r requirements.txt
Run the GUI

bash
python uflix_gui.py
Default Password

uflix123
🗂 Folder Structure
Uflix_Scraper/
│
├── uflix_gui.py         # Main GUI launcher
├── main.py              # Scraper logic
├── api.py               # REST API server
├── dashboard.html       # Frontend UI
│
├── logs/
│   └── history.json     # Scrape log history
├── data/
│   └── movies.json      # Exported movie metadata
├── builds/              # Exported ZIP bundles
└── settings.json        # Saved password
🧠 Credits & Roadmap
This project is under development by @marese310 — still in beta. Plans include:

[ ] Telegram alert integration

[ ] Headless scrape mode

[ ] Light/dark GUI themes

[ ] One-click .exe export

⚠️ Disclaimer
This tool is intended for educational and personal automation use. You are responsible for how you use or distribute scraped content. Respect site terms and robots.txt policies.
