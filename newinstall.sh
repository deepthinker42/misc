#!/bin/bash

sudo dnf install -y wget

wget https://github.com/balena-io/etcher/releases/download/v1.5.113/balena-etcher-electron-1.5.113-linux-ia32.zip
unzip balena-etcher-electron-1.5.113-linux-ia32.zip
chmod 755 balena-etcher-electron-1.5.113-linux-ia32.zip
./balena-etcher-electron-1.5.113-x64.AppImage

sudo dnf install -y fedora-workstation-repositories
sudo dnf config-manager --set-enabled google-chrome
sudo dnf install -y google-chrome-stable

sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://brave-browser-rpm-release.s3.brave.com/x86_64/
sudo rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc
sudo dnf install -y brave-browser

sudo dnf group install -y --with-optional virtualization
sudo systemctl start libvirtd
sudo systemctl enable libvirtd

sudo dnf group install -y "Administration Tools" "Audio Production" "Container Management" "Development Tools" "D Development Tools and Libraries" "Games and Entertainment" "RPM Development Tools" "System Tools"
sudo dnf install -y golang
sudo dnf install -y npm
sudo dnf install -y kubernetes ansible kubernetes-ansible kubernetes-kubeadm

sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
cat << EOF | sudo tee /etc/yum.repos.d/vscode.repo
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF
sudo dnf check-update
sudo dnf install -y code

#
