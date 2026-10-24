#!/usr/bin/env bash

# Copyright (c) 2021-2026 community-scripts ORG
# Author: brunoz78
# License: MIT | https://github.com/community-scripts/ProxmoxVED/raw/main/LICENSE
# Source: https://github.com/brunoz78/Tautulli

source /dev/stdin <<<"$FUNCTIONS_FILE_PATH"
color
verb_ip6
catch_errors
setting_up_container
network_check
update_os

msg_info "Installing Dependencies"
# Tautulli ships its Python libraries in lib/, so the system Python is enough.
$STD apt install -y python3 python3-openssl ca-certificates tzdata
msg_ok "Installed Dependencies"

fetch_and_deploy_gh_release "Tautulli" "brunoz78/Tautulli" "tarball"

msg_info "Configuring Tautulli"
# version.txt and branch.txt tell the built-in updater where it stands.
get_latest_github_release "brunoz78/Tautulli" "false" >/opt/Tautulli/version.txt
echo "master" >/opt/Tautulli/branch.txt
mkdir -p /config
chmod 700 /config
msg_ok "Configured Tautulli"

msg_info "Creating Service"
cat <<EOF >/etc/systemd/system/tautulli.service
[Unit]
Description=Tautulli
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/Tautulli
Environment=TAUTULLI_UI_LANG=de
Environment=TZ=Europe/Zurich
ExecStart=/usr/bin/python3 /opt/Tautulli/Tautulli.py --datadir /config --config /config/config.ini --nolaunch --quiet
KillSignal=SIGINT
TimeoutStopSec=20
Restart=on-failure
RestartSec=5
SyslogIdentifier=tautulli
# No ProtectSystem/ReadWritePaths: the built-in updater unpacks into /config/update
# and renames the files into /opt/Tautulli, which fails across separate bind mounts.
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
EOF
systemctl enable -q --now tautulli
msg_ok "Created Service"

motd_ssh
customize
cleanup_lxc
