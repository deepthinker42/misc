#!/bin/bash

sudo dnf install -y wget

wget https://github.com/balena-io/etcher/releases/download/v1.5.113/balena-etcher-electron-1.5.113-linux-ia32.zip
unzip balena-etcher-electron-1.5.113-linux-ia32.zip
chmod 755 balena-etcher-electron-1.5.113-linux-ia32.zip
./balena-etcher-electron-1.5.113-x64.AppImage

sudo dnf install -y fedora-workstation-repositories
sudo dnf config-manager --set-enabled google-chrome
sudo dnf install -y google-chrome-stable
