import subprocess
import json
import os
import time
from datetime import datetime

SERVERS = {
    "Google": "8.8.8.8",
    "YouTube": "youtube.com",
    "Valorant": "99.83.136.104"
}
DATA_FILE = "data.json"

def get_ping(host):
    try:
        # Pings the host once. Windows uses -n, Linux/Mac uses -c. 
        # Adjust '-c' to '-n' if you are running this on a Windows machine.
        output = subprocess.check_output(['ping', '-c', '1', '-W', '2', host], universal_newlines=True)
        for line in output.split('\n'):
            if 'time=' in line:
                time_ms = line.split('time=')[1].split(' ')[0]
                return float(time_ms)
    except Exception:
        pass
    return None

def track_and_push():
    # Load existing data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Collect new data
    entry = {"timestamp": datetime.utcnow().isoformat() + "Z"}
    for name, host in SERVERS.items():
        entry[name] = get_ping(host)

    data.append(entry)
    data = data[-288:] # Keep the last 48 hours (if running every 10 mins)

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    # Push to GitHub automatically
    try:
        subprocess.run(['git', 'add', DATA_FILE], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['git', 'commit', '-m', 'Auto-update local ping'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['git', 'push'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushed new local ping data to GitHub.")
    except subprocess.CalledProcessError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed to push to GitHub. Will try again next cycle.")

if __name__ == "__main__":
    print("Starting local ping tracker... Press Ctrl+C to stop.")
    while True:
        track_and_push()
        time.sleep(600) # Waits 600 seconds (10 minutes) before running again
