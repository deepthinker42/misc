#!/bin/bash

sudo sed -i "s/UBUNTU_VER\ \=\ 18\ \]/& \|\|\ [\ \$UBUNTU_VER\ \=\ 19 \]/" /usr/local/pulse/PulseClient_x86_64.sh
sudo ./PulseClient_x86_64.sh install_dependency_packages
sudo mkdir /usr/local/pulse/extra /usr/local/pulse/debs
sudo wget -O /usr/local/pulse/debs/libicu60_60.2-3ubuntu3_amd64.deb http://archive.ubuntu.com/ubuntu/pool/main/i/icu/libicu60_60.2-3ubuntu3_amd64.deb
sudo wget -O /usr/local/pulse/debs/libjavascriptcoregtk-1.0-0_2.4.11-4_amd64.deb http://archive.ubuntu.com/ubuntu/pool/universe/w/webkitgtk/libjavascriptcoregtk-1.0-0_2.4.11-4_amd64.deb
sudo wget -O /usr/local/pulse/debs/libwebkitgtk-1.0-0_2.4.11-4_amd64.deb http://archive.ubuntu.com/ubuntu/pool/universe/w/webkitgtk/libwebkitgtk-1.0-0_2.4.11-4_amd64.deb
sudo dpkg -x /usr/local/pulse/debs/libicu60_60.2-3ubuntu3_amd64.deb /usr/local/pulse/extra
sudo dpkg -x /usr/local/pulse/debs/libjavascriptcoregtk-1.0-0_2.4.11-4_amd64.deb /usr/local/pulse/extra
sudo dpkg -x /usr/local/pulse/debs/libwebkitgtk-1.0-0_2.4.11-4_amd64.deb /usr/local/pulse/extra
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/pulse/extra/usr/lib/x86_64-linux-gnu/' >> ~/.bashrc
echo 'export PATH=${PATH}:/usr/local/pulse' >> ~/.bashrc
