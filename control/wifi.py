import subprocess, re

def disconnect_wifi():
    """Disconnect from current Wi-Fi network."""
    try:
        subprocess.run(["nmcli", "device", "disconnect", "wlan0"], check=True)
        print("Wi-Fi disconnected.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Disconnect failed: {e}")
        return False


def get_connection_info(interface):
    """Return IP address, gateway, and DNS for wlan0"""
    try:
        output = subprocess.check_output(['nmcli', '-t', 'device', 'show', interface], encoding='utf-8')
        data = {}
        for line in output.splitlines():
            if line.startswith("IP4.ADDRESS[1]:"):
                data["ip"] = line.split(":")[1].strip().split("/")[0]
            elif line.startswith("IP4.GATEWAY:"):
                data["gateway"] = line.split(":")[1].strip()
            elif line.startswith("IP4.DNS[1]:"):
                data["dns"] = line.split(":")[1].strip()
        return data
    except subprocess.CalledProcessError:
        return {}

