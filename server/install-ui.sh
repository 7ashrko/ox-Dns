#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run as root"; exit 1; }

apt-get update
apt-get install -y python3 python3-venv

install -d -m 0755 /opt/ps4-dns/app
cp -r "$(dirname "$0")/../app/"* /opt/ps4-dns/app/
cp "$(dirname "$0")/../server/unbound.conf" /opt/ps4-dns/unbound.conf
cp "$(dirname "$0")/../server/ps4-blocklist.conf" /opt/ps4-dns/ps4-blocklist.conf

# Keep the existing Unbound setup if present; otherwise install the project config.
if ! command -v unbound >/dev/null 2>&1; then
  apt-get install -y unbound
fi

if [ ! -f /etc/unbound/unbound.conf ]; then
  cp /opt/ps4-dns/unbound.conf /etc/unbound/unbound.conf
  cp /opt/ps4-dns/ps4-blocklist.conf /etc/unbound/ps4-blocklist.conf
fi

python3 -m venv /opt/ps4-dns/venv
/opt/ps4-dns/venv/bin/pip install --upgrade pip flask

cat >/etc/systemd/system/ps4-dns-ui.service <<'EOF'
[Unit]
Description=PS4 DNS Control Center
After=network-online.target unbound.service
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ps4-dns/app
Environment=SECRET_KEY=CHANGE_THIS_SECRET
ExecStart=/opt/ps4-dns/venv/bin/python /opt/ps4-dns/app/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now ps4-dns-ui

echo
echo "PS4 DNS UI installed."
echo "Open: http://VPS_IP:8080"
echo "IMPORTANT: restrict port 8080 to your home public IP:"
echo "  ufw allow from YOUR_HOME_PUBLIC_IP to any port 8080 proto tcp"
