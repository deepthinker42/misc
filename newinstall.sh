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

a
