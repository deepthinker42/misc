#!/usr/bin/env python

import os
import sys
import argparse
import json
import requests
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen


USERNAME = 'ADMIN'
PASSWORD = 'ADMIN'


class PyBMC(object):

    def __init__(self, args):
        self.bmc_agent = args.bmc_agent
        self.session_token = None
        self.url_base = 'http://%s' % self.bmc_agent
        return

    def login(self):
        retval = True
        url = self.url_base
        payload = {'username': USERNAME, 'password': PASSWORD}
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        self.session = requests.session()
        response = self.session.post(url, data=payload, headers=headers, verify=False)
        print(response.headers)
        print(response.cookies)
        if response.status_code == 200:
            print('Logged in')
            self.session_token = response.text
        else:
            print('Failed to log into "%s": %s' % (self.url_base, str(response.status_code)))
            retval = False
        return retval

    def logout(self):
        url = '%s/cgi/logout.cgi' % self.url_base
        return True

    def main(self):
        if not self.login():
            return 1
        if not self.logout():
            return 1
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BMC Agent for Python')
    parser.add_argument('-b', '--bmc-agent', help='BMC agent to connect to')
    args = parser.parse_args()

    PYBMC = PyBMC(args)
    rc = PYBMC.main()
    exit(rc)
