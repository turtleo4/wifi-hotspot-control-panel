from flask import Flask, render_template, request, redirect
import subprocess
import json
import os
from control.wifi import disconnect_wifi, get_connection_info

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

KNOWN_NETWORKS_FILE = 'known_networks.json'

# Ensure known networks file exists
if not os.path.exists(KNOWN_NETWORKS_FILE):
    with open(KNOWN_NETWORKS_FILE, 'w') as f:
        json.dump({}, f)

def load_known_networks():
    with open(KNOWN_NETWORKS_FILE, 'r') as f:
        return json.load(f)

def save_known_network(ssid, password):
    networks = load_known_networks()
    networks[ssid] = password
    with open(KNOWN_NETWORKS_FILE, 'w') as f:
        json.dump(networks, f)

def scan_wifi():
    try:
        output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi'], encoding='utf-8')
        networks = []
        for line in output.strip().split('\n'):
            parts = line.strip().split(':')
            if len(parts) >= 2:
                ssid, signal = parts[0], parts[1]
                security = parts[2] if len(parts) > 2 else ""
                if ssid:
                    networks.append({"ssid": ssid, "signal": int(signal), "secure": bool(security)})
        return networks
    except subprocess.CalledProcessError:
        return []

def get_current_connection():
    try:
        output = subprocess.check_output(['nmcli', '-t', '-f', 'NAME,DEVICE', 'con', 'show', '--active'], encoding='utf-8')
        for line in output.strip().split('\n'):
            parts = line.split(':')
            if len(parts) == 2 and parts[1].startswith('wl'):
                return parts[0]  # SSID
    except subprocess.CalledProcessError:
        return None
    return None

@app.route('/', methods=['GET'])
def index():
    scanned = scan_wifi()
    known = load_known_networks()
    current = get_current_connection()
    info_wifi_0 = get_connection_info('wlan0') if current else {}
    info_wifi_1 = get_connection_info('wlan1') if current else {}
    info_wifi_2 = get_connection_info('wlan2') if current else {}
    info_eth = get_connection_info('eth0') if current else {}

    known_visible = {}
    known_hidden = []

    # Match known networks against scan results
    scanned_ssids = {net['ssid'] for net in scanned}
    for ssid, pwd in known.items():
        if ssid in scanned_ssids:
            known_visible[ssid] = pwd
        else:
            known_hidden.append(ssid)

    # Remove known-visible from the available list
    networks = [n for n in scanned if n['ssid'] not in known_visible]

    return render_template('index.html',
                           networks=networks,
                           known_visible=known_visible,
                           known_hidden=known_hidden,
                           current=current,
                           netinfo_wifi_0=info_wifi_0,
                           netinfo_wifi_1=info_wifi_1,
                           netinfo_wifi_2=info_wifi_2,
                           netinfo_eth=info_eth)

@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    save = request.form.get('save') == 'on'

    try:
        cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid]
        if password:
            cmd += ['password', password]
        subprocess.check_output(cmd)
        if save:
            save_known_network(ssid, password or '')
        return redirect('/')
    except subprocess.CalledProcessError:
        return "Failed to connect", 500

@app.route("/disconnect", methods=["POST"])
def disconnect():
    success = disconnect_wifi()
    # Optionally clear session or state to reset UI
    if success:
        print("Disconnect successful")
    else:
        print("Disconnect failed")
    return redirect("/")

import traceback

# @app.errorhandler(500)
# def internal_error(e):
#     tb = traceback.format_exc()
#     app.logger.error("500 error: %s\n%s", e, tb)
#     return "Internal Server Error", 500

@app.route('/status', methods=['GET'])
def get_status():
    scanned = scan_wifi()
    known = load_known_networks()
    current = get_current_connection()
    info_wifi = get_connection_info('wlan0') if current else {}
    info_eth = get_connection_info('eth0') if current else {}

    # Hide known from scanned
    known_visible = []
    known_hidden = []
    scanned_ssids = [net['ssid'] for net in scanned]
    for ssid, pwd in known.items():
        if ssid in scanned_ssids:
            known_visible.append({ "ssid": ssid, "password": pwd })
        else:
            known_hidden.append(ssid)

    return jsonify({
        "scanned": scanned,
        "known_visible": known_visible,
        "known_hidden": known_hidden,
        "current": current,
        "wifi": info_wifi,
        "eth": info_eth,
    })
