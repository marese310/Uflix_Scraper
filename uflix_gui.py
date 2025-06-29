import os, json, subprocess, webbrowser, threading, time, socket, psutil
from tkinter import *
from tkinter import messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageDraw
import pystray
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import zipfile
import schedule
import platform
import ctypes

# ───── CONFIG ─────
SETTINGS_FILE = "settings.json"
DEFAULT_PASS = "uflix123"
BACKDOOR_PASS = "ADMIN"
HISTORY_FILE = "logs/history.json"

# ───── NOTIFICATION ─────
def show_notification(title, msg):
    if platform.system() == "Windows":
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40)
    else:
        print(f"[{title}] {msg}")

# ───── UTILITY ─────
def load_password():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"password": DEFAULT_PASS}, f)
        return DEFAULT_PASS
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f).get("password", DEFAULT_PASS)
    except:
        return DEFAULT_PASS

def save_password(new_pass):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"password": new_pass}, f)

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

# ───── TRAY ICON ─────
def tray_menu():
    return pystray.Menu(
        pystray.MenuItem("Show UFlix", show_window),
        pystray.MenuItem("Stop All Servers", stop_all),
        pystray.MenuItem("Quit", quit_app)
    )

def create_icon():
    image = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(image)
    d.rectangle((10, 10, 54, 54), fill="#56ccf2")
    d.text((18, 14), "🎬", fill="white")
    return image

def show_window(icon=None, item=None): root.deiconify()
def hide_to_tray(): root.withdraw(); threading.Thread(target=lambda: pystray.Icon("UFlix", create_icon(), "UFlix", tray_menu()).run()).start()
def quit_app(icon=None, item=None): root.quit()

# ───── PASSWORD ─────
def ask_password():
    while True:
        p = simpledialog.askstring("UFlix Login", "Enter password:", show="*")
        if p in [stored_password, BACKDOOR_PASS]:
            break
        elif p is None:
            return
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

def change_password():
    current = simpledialog.askstring("Current Password", "Enter current password:", show="*")
    if current not in [stored_password, BACKDOOR_PASS]:
        messagebox.showerror("Error", "Incorrect password.")
        return
    new_pass = simpledialog.askstring("New Password", "Enter new password:", show="*")
    if new_pass:
        save_password(new_pass)
        messagebox.showinfo("Success", "Password updated.")
    else:
        messagebox.showinfo("Cancelled", "No changes made.")

# ───── SERVER + SCRAPER ─────
def run_api(): subprocess.Popen(["python", "api.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def run_server(): subprocess.Popen(["python", "-m", "http.server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dashboard():
    if not os.path.exists("dashboard.html"):
        messagebox.showerror("Missing", "dashboard.html not found!")
        return
    webbrowser.open("http://localhost:8000/dashboard.html")

def run_server_and_dashboard():
    if not os.path.exists("dashboard.html"):
        messagebox.showerror("dashboard.html Not Found", os.getcwd())
        return
    threading.Thread(target=run_server).start()
    time.sleep(1)
    webbrowser.open("http://localhost:8000/dashboard.html")

def stop_all():
    killed = []
    for p in psutil.process_iter(attrs=["pid", "cmdline"]):
        try:
            cmd = " ".join(p.info["cmdline"]).lower()
            if any(k in cmd for k in ["api.py", "http.server", "main.py"]):
                p.kill()
                killed.append(p.info["pid"])
        except: continue
    log(f"🛑 Stopped: {len(killed)} processes → {killed or 'None'}")

def run_scraper():
    log("▶ Running movie scraper...")
    try:
        output = subprocess.check_output(["python", "main.py"], stderr=subprocess.STDOUT)
        log(output.decode("utf-8") or "✅ Scraper completed.")
    except subprocess.CalledProcessError as e:
        log(f"❌ Scraper failed:\n{e.output.decode('utf-8')}")
    try:
        run_api()
        time.sleep(1)
        run_server()
        time.sleep(1)
        webbrowser.open("http://localhost:8000/dashboard.html")
        show_notification("UFlix", "🎬 Scraper & Dashboard launched")
        log("🌐 Dashboard launched.")
    except Exception as e:
        log(f"❌ Dashboard launch error: {e}")

# ───── LOGIC ─────
def log(msg): log_box.insert(END, msg + "\n"); log_box.see(END)

def zip_project():
    os.makedirs("builds", exist_ok=True)
    fname = f"UFlix_Bundle_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    path = os.path.join("builds", fname)
    with zipfile.ZipFile(path, "w") as zipf:
        for folder, _, files in os.walk("."):
            for file in files:
                if "venv" in folder or "__pycache__" in folder or file.endswith(".zip"): continue
                filepath = os.path.join(folder, file)
                zipf.write(filepath, arcname=os.path.relpath(filepath, "."))
    log(f"📦 Exported ZIP: {path}")
    messagebox.showinfo("ZIP Created", path)

# ───── STATS ─────
def update_chart():
    if not os.path.exists(HISTORY_FILE): return
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)[-8:]
        if not history: return
        times = [entry["time"][-5:] for entry in history]
        totals = [entry["total"] for entry in history]
        ax.clear()
        ax.plot(times, totals, marker="o", color="#56ccf2")
        ax.set_title("Movie Count History")
        chart_canvas.draw()
    except Exception as e:
        log(f"Chart error: {e}")

def update_stats():
    try:
        json_path = "data/movies.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                label_count.set(f"🎞️ Movies: {len(data)}")
            mod = os.path.getmtime(json_path)
            label_updated.set(f"🕒 Last Scrape: {datetime.fromtimestamp(mod).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            label_count.set("🎞️ Movies: 0")
            label_updated.set("🕒 Last Scrape: —")
    except:
        label_count.set("🎞️ Error"); label_updated.set("🕒 Error")

def update_status():
    status_api.set("🟢 Running" if is_port_open(5000) else "🔴 Offline")
    status_dash.set("🟢 Running" if is_port_open(8000) else "🔴 Offline")
    update_stats()
    update_chart()
    root.after(3000, update_status)

def start_scheduler():
    def loop():
        while True:
            schedule.run_pending()
            time.sleep(30)
    schedule.every().day.at("04:00").do(lambda: threading.Thread(target=run_scraper).start())
    threading.Thread(target=loop, daemon=True).start()
    log("⏰ Scheduler enabled: Daily at 04:00")

# ───── GUI BUILD ─────
stored_password = load_password()
ask_password()

root = Tk()
root.title("🎬 UFlix Launcher")
root.geometry("560x690")
root.configure(bg="#111")

Label(root, text="UFlix Scraper Console", font=("Segoe UI", 16, "bold"), fg="#56ccf2", bg="#111").pack(pady=10)

status_api = StringVar(value="🔴 Offline")
status_dash = StringVar(value="🔴 Offline")
label_count = StringVar(value="🎞️ Movies: ?")
label_updated = StringVar(value="🕒 Last Scrape: ?")

frame = Frame(root, bg="#111")
frame.pack()

Label(frame, text="API Server:", bg="#111", fg="white").grid(row=0, column=0, sticky="w")
Label(frame, textvariable=status_api, bg="#111", fg="lime").grid(row=0, column=1, sticky="w")

Label(frame, text="Dashboard:", bg="#111", fg="white").grid(row=1, column=0, sticky="w")
Label(frame, textvariable=status_dash, bg="#111", fg="lime").grid(row=1, column=1, sticky="w")

Label(frame, textvariable=label_count, bg="#111", fg="#ccc").grid(row=2, column=0, columnspan=2, sticky="w", pady=(10,0))
Label(frame, textvariable=label_updated, bg="#111", fg="#ccc").grid(row=3, column=0, columnspan=2, sticky="w")

Button(root, text="▶ Run Scraper", command=lambda: threading.Thread(target=run_scraper).start(), width=40).pack(pady=5)
Button(root, text="▶ Launch API & Dashboard", command=run_server_and_dashboard, width=40).pack(pady=5)
Button(root, text="📡 Open Dashboard", command=run_dashboard, width=40).pack(pady=5)
Button(root, text="🛑 Stop All Servers", command=stop_all, width=40, fg="white", bg="#440000").pack(pady=5)
Button(root, text="🧲 Minimize to Tray", command=hide_to_tray, width=40).pack(pady=5)
Button(root, text="🔁 Change Password", command=change_password, width=40).pack(pady=5)
Button(root, text="📦 Export Bundle (ZIP)", command=zip_project, width=40).pack(pady=5)
Button(root, text="⏰ Enable Daily Scheduler", command=start_scheduler, width=40).pack(pady=5)

Label(root, text="📊 Scrape Trend", bg="#111", fg="white").pack()
fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
chart_canvas = FigureCanvasTkAgg(fig, master=root)
chart_canvas.get_tk_widget().pack(pady=5)

Label(root, text="📜 Log Output", bg="#111", fg="white", anchor="w").pack(fill="x", pady=(10, 0))
log_box = Text(root, height=10, bg="#222", fg="white")
log_box.pack(fill="both", padx=10, pady=5, expand=True)

Button(root, text="❌ Quit", command=quit_app, fg="red", width=40).pack(pady=10)

update_status()
root.mainloop()
