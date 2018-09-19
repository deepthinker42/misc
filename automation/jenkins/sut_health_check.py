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
        self.host = args.host if args.host else 'sqa-jenkins'
        self.port = args.port if args.port else 8080
        self.url = 'http://%s:%d' % (self.host, self.port)
        self.password = getpass.getpass()
        self.server = jenkins.Jenkins(self.url, username='rgoodman', password=self.password.strip())
        return

    def getBMCIP(self, computer):
        bmc_ip = None
        job = self.server.get_job('computer')
        config = job.get_config()
        lines = [line.strip() for line in config.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if 'value="BMC_IP"' in line:
                bmc_ip = lines[i+1].split('value="', 1)[1].split('"', 1)[0].strip()
        return bmc_ip

    def getComputers(self, params='_class,displayName,offline'):
        url = '%s/computer/api/json?tree=computer[%s]' % (self.url, params)
        try:
            response = urlopen(url, timeout=5)
        except Exception as e:
            print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
            return
        data = json.loads(response.read())
        if not 'computer' in data:
            print('ERROR: No computers found')
            return
        computers = {}
        for computer in data['computer']:
            computers[computer['displayName']] = not computer['offline']
        return computers

    def getHostName(self, computer):
        host_name = None
        url = '%s/computer/%s/' % (self.url, computer)
        try:
            response = urlopen(url, timeout=5)
        except Exception as e:
            print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
            return
        data = response.read()
        if 'Computer: ' in data:
            lines = [line.strip() for line in data.splitlines() if line.strip()]
            for i, line in enumerate(lines):
                if 'Computer:' in line and 'Username:' in line:
                    host_name = line.split('Computer: ', 1)[1].split(' ', 1)[0].strip()
                    return host_name
        job = self.server.get_job(computer)
        config = job.get_config()
        lines = [line.strip() for line in config.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if 'Computer:' in line and 'Username:' in line:
                host_name = line.split('Computer: ', 1)[1].split(' ', 1)[0].strip()
        return host_name

    def nslookup(self, name=None, ip=None):
        value = None
        if name:
            try:
                output = subprocess.check_output('nslookup "%s" | grep "Address: " | tail -1' % name, shell=True)
                if 'Address: ' in output:
                    value = output.split(' ', 1)[1].strip()
            except Exception as e:
                pass
        elif ip:
            try:
                output = subprocess.check_output('nslookup "%s" | grep "name = " | tail -1' % name, shell=True)
                if 'name = ' in output:
                    value = output.split('name = ', 1)[1].split('.', 1)[0].strip()
            except Exception as e:
                pass
            return value

    def main(self):
        ips = {}
        computers = self.getComputers()
        for computer in computers:
            if not 'diesel' in computer and not 'ethanol' in computer and not 'goldengoose' in computer and not 'grandstand' in computer and not 'SUT' in computer:
                continue
            ip = self.nslookup(computer)
            if ip and '.' in ip:
                ips[computer] = ip
                break
            ip = self.getBMCIP(computer)
            if ip:
                ips[computer] = ip
                break
            ip = self.nslookup(self.getHostName(computer))
            if ip:
                ips[computer] = ip
            else:
                ips[computer] = 'unknown'
        for computer, ip in sorted(ips.items()):
            print('%-20s  %s' % (computer, ip))
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SUT Health Check')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    SHC = SUTHealthCheck(args)
    if not SHC.main():
        exit(1)

