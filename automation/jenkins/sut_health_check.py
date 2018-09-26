#!/usr/bin/env python

import sys
import jenkins
import json
import traceback
import datetime
import time
import subprocess
import argparse
import getpass
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen


class SUTHealthCheck(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.url = 'http://%s:%d' % (self.host, self.port)
        self.server = jenkins.Jenkins(self.url, username=getpass.getuser(), password=getpass.getpass().strip())
        return

    def getBMCIP(self, computer):
        bmc_ip = None
        try:
            config = self.server.get_node_config(computer)
        except:
            return bmc_ip
        lines = [line.strip() for line in config.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if 'bmc_ip' in line.lower():
                bmc_ip = lines[i+1].split('>', 1)[1].split('<', 1)[0].strip()
                break
            if 'SUT' in computer and '<description>' in line and 'omputer' in line:
                bmc_ip = line.split('omputer', 1)[1].split(':', 1)[1].strip().split(' ', 1)[0].strip()
                break
        return bmc_ip

    def getComputers(self):
        computers = {}
        nodes = self.server.get_nodes()
        for entry in nodes:
            name = entry['name']
            if 'diesel' in name or 'ethanol' in name or 'goldengoose' in name or 'grandstand' in name or 'SUT' in name:
                computers[name] = not entry['offline']
        return computers

    def getHostName(self, computer):
        host_name = None
        try:
            config = self.server.get_node_config(computer)
        except:
            print('coult not get node_config for %s' % computer)
            return host_name
        lines = [line.strip() for line in config.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if 'SUT' in computer and '<description>' in line and 'omputer' in line:
                host_name = line.split('omputer', 1)[1].split(' ', 2)[1].strip()
                return host_name
        return host_name

    def nslookup(self, name=None, ip=None):
        value = None
        if name:
            try:
                cmd = 'nslookup "%s" | grep "Address: " | tail -1' % name
                output = subprocess.check_output(cmd, shell=True)
                if not 'can\'t find' in output and 'Address: ' in output:
                    value = output.split(' ', 1)[1].strip()
            except Exception as e:
                print('ERROR: nslookup failed for "%s": %s\n%s' % (name, e, traceback.format_exc(e)))
        elif ip:
            try:
                cmd = 'nslookup "%s" | grep "name = " | tail -1' % ip
                output = subprocess.check_output(cmd, shell=True)
                if 'name = ' in output:
                    value = output.split('name = ', 1)[1].split('.', 1)[0].strip()
            except Exception as e:
                print('ERROR: nslookup failed for "%s": %s\n%s' % (name, e, traceback.format_exc(e)))
        return value

    def main(self):
        ips = {}
        computers = self.getComputers()
        for computer in computers:
            ipaddr = self.nslookup(name=computer)
            if ipaddr and '.' in ipaddr:
                ips.setdefault(computer, {'ip': ipaddr})
                ips[computer]['name'] = self.nslookup(ip=ipaddr)
                continue
            ipaddr = self.getBMCIP(computer)
            if ipaddr:
                if '.' in ipaddr:
                    ips.setdefault(computer, {'ip': ipaddr})
                    ips[computer]['name'] = self.nslookup(ip=ipaddr)
                else:
                    ips.setdefault(computer, {'name': ipaddr})
                    ips[computer]['ip'] = self.nslookup(name=ipaddr)
            else:
                ips.setdefault(computer, {'ip': 'unknown', 'name': computer})
        for computer, data in sorted(ips.items()):
            print('%-20s  %s (%s)' % (computer, data['ip'], data['name'].lower()))
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SUT Health Check')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    SHC = SUTHealthCheck(args)
    if not SHC.main():
        exit(1)

