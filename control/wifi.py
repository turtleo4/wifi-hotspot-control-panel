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
    try:
        output = subprocess.check_output(
            ['nmcli', '-t', '-f', 'IN-USE,SSID,SIGNAL', 'dev', 'wifi'],
            encoding='utf-8'
        )

        current_ssid = None
        signal = 0
        for line in output.strip().split('\n'):
            if line.startswith('*'):
                _, ssid, signal = line.split(':')
                current_ssid = ssid
                break

        def safe_extract(field):
            try:
                raw = subprocess.check_output(
                    ['nmcli', '-t', '-f', field, 'device', 'show', interface],
                    encoding='utf-8'
                ).strip()
                parts = raw.split(':')
                return parts[1].strip() if len(parts) > 1 else None
            except subprocess.CalledProcessError:
                return None

        ip = safe_extract('IP4.ADDRESS')
        gateway = safe_extract('IP4.GATEWAY')
        dns_raw = subprocess.check_output(
            ['nmcli', '-t', '-f', 'IP4.DNS', 'device', 'show', interface],
            encoding='utf-8'
        ).strip().split('\n')
        dns_list = [line.split(':')[1].strip() for line in dns_raw if ':' in line]

        return {
            "ssid": current_ssid,
            "signal": int(signal),
            "ip": ip,
            "gateway": gateway,
            "dns": dns_list
        }

    except subprocess.CalledProcessError:
        return {}

