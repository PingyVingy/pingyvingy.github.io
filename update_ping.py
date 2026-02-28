import subprocess
import json
import os
from datetime import datetime

# The servers you want to monitor
SERVERS = {
    "Google": "8.8.8.8",
    "YouTube": "youtube.com",
    "Valorant": "99.83.136.104"
}
DATA_FILE = "data.json"

def get_ping(host):
    try:
        # Pings the host once with a 2-second timeout (Linux format for GitHub runners)
        output = subprocess.check_output(['ping', '-c', '1', '-W', '2', host], universal_newlines=True)
        for line in output.split('\n'):
            if 'time=' in line:
                # Extract the time in milliseconds
                time_ms = line.split('time=')[1].split(' ')[0]
                return float(time_ms)
    except Exception:
        pass
    return None # Return None if ping fails

# Load existing data or start fresh
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

# Limit to the last 288 data points (e.g., 48 hours of data if pinging every 10 minutes)
data = data[-288:]

with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=2)
