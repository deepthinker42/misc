#!/usr/bin/env python

import argparse
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen
from utils import connect, getActiveJobs


class ActiveJobs(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.username = args.username
        self.password = args.password
        self.server = None
        return

    def main(self):
        url = 'http://%s:%d' % (self.host, self.port)
        self.server = connect(url, self.username, self.password)
        if not self.server:
            return False
        active_jobs = getActiveJobs(self.server)
        self.showActiveJobs(active_jobs)
        return True

    def showActiveJobs(self, active_jobs):
        if active_jobs:
            print('\nPrevious Build Status  Job')
            print('---------------------  ----------------------------------')
            for url, color in active_jobs:
                name = url.replace('/', ' ').strip().split(' ')[-1]
                print('%-21s  %s' % (color, name))
        else:
            print('There are no active jobs')
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get list of active Jenkins jobs')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    parser.add_argument('-u', '--username', help='Jenkins master login username')
    parser.add_argument('-P', '--password', help='Jenkins master login password')
    args = parser.parse_args()
    AJ = ActiveJobs(args)
    if not AJ.main():
        exit(1)

