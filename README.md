# 🛠️ NanoPi Wi-Fi Hotspot Control Panel

A lightweight, Flask-based web interface for managing Wi-Fi connections on a NanoPi Zero2 (or any Debian-based Linux system). This control panel allows you to manually connect to, disconnect from, and manage known Wi-Fi networks via a web interface — without needing to use the command line.

---

## 📦 Features

- Scan and display nearby Wi-Fi networks with signal strength and encryption status
- Manual connection to both open and secured Wi-Fi networks
- Toggle password field based on security
- Save known networks for future use
- View current Wi-Fi connection info (IP, gateway, DNS)
- Disconnect from current network without forgetting it
- Clean Bootstrap-based UI with Material Design icons
- Flask + Gunicorn + NGINX stack (no Docker required)

---

## ⚙️ Requirements

Tested on: **NanoPi Zero2 running Armbian (Debian-based)**  
Minimum hardware: 2G RAM recommended

### Prerequisites

Ensure the following are installed before setup:

See [requirements.txt](requirements.txt)

### Python Packages

Create a virtual environment and install dependencies:

``` bash
sudo apt update
sudo apt install python3-pip python3-venv nginx network-manager -y

# Setup project
cd /wwww-data/
git clone https://github.com/turtleo4/wifi-hotspot-control-panel.git
cd wifi-hotspot-control-panel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

## 🚀 Running the App

### Gunicorn (via systemd)

Create a systemd service:

#### /etc/systemd/system/wifi-hotspot-control-panel.service
``` bash
[Unit]
Description=Gunicorn instance to serve NanoPi Control Panel
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/www-data/wifi-hotspot-control-panel
ExecStart=/www-data/wifi-hotspot-control-panel/venv/bin/gunicorn -w 3 -b localhost:8000 app:app

[Install]
WantedBy=multi-user.target
```

``` bash
# Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable wifi-hotspot-control-panel
sudo systemctl start wifi-hotspot-control-panel
```
### NGINX

Create a site configuration:

#### /etc/nginx/sites-available/wifi-hotspot-control-panel
``` bash
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /www-data/wifi-hotspot-control-panel/static/;
    }
}
```
#### Enable it:
``` bash
sudo ln -s /etc/nginx/sites-available/wifi-hotspot-control-panel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📂 Project Structure
``` bash
wifi-hotspot-control-panel/
├── app.py
├── control/
│   └── wifi.py
├── static/
│   ├── css/
│   │   └── styles.css
│   └── bootstrap.min.css
├── templates/
│   └── index.html
├── known_networks.json
├── requirements.txt
└── README.md
```


## 🔒 Security Notes
- This tool should only be accessible on trusted local networks or behind authentication.
- No auto-connect is implemented to prevent accidental exposure.
- Passwords are stored in plain JSON (known_networks.json). Consider encrypting or restricting access if needed.

## Screenshot

![Image](static/img/favicon.png)
