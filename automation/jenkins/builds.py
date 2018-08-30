#!/usr/bin/env python

import sys
import argparse
import time
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen
from utils import connect, getJobNames, getBuilds, nslookup


class Builds(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.days = args.days
        self.search = args.search
        self.specific_job = args.job
        self.specific_build = args.build
        self.url = 'http://%s:%d' % (self.host, self.port)
        return

    def main(self):
        job_names = [self.specific_job] if self.specific_job else getJobNames(self.host, self.port)
        if not job_names:
            return False
        print('Looking through %d jobs' % len(job_names))
        builds = getBuilds(self.url, job_names, self.days, self.search, self.specific_job, self.specific_build)
        print('%d builds in the last %d day(s)' % (len(builds), self.days))
        if not builds:
            return False
        self.showBuilds(builds)
        return True

    def showBuilds(self, builds):
        s = 'All builds' if not self.specific_job else ('%s builds' % self.specific_job)
        s += ' in the last %d days' % self.days
        s += ':' if not self.search else (' with "%s" in the console output:' % self.search)
        print(s)
        time_start = time.time()
        num_builds = len(builds)
        for i, build in enumerate(builds):
            url = build[0]
            ts = build[1]
            time_str = time.strftime('%Y-%m-%d %H:%M:%S %a', time.localtime(ts))
            console_url = url + 'console'
            if self.search:
                failed_hosts = {}
                try:
                    response = urlopen(console_url, timeout=15)
                    lines = response.readlines()
                    error = None
                    for line in lines:
                        line = line.strip()
                        if not error and (': error ' in line or ': fatal error ' in line):
                            error = line.split('</span>', 1)[1]
                        if not self.search in line:
                            if 'FATAL: Remote call on' in line:
                                ip = line.split('to /', 1)[1].split(' ', 1)[0]
                                failed_hosts.setdefault(nslookup(ip), True)
                            continue
                        if 'Cannot contact ' in line:
                            failed_hosts.setdefault(line.split('Cannot contact ', 1)[1].split(':', 1)[0], True)
                        elif '/' in line:
                            try:
                                failed_hosts.setdefault(nslookup(line.rsplit('/', 1)[1].rsplit(' ')[0].rsplit(':')[0]), True)
                            except:
                                failed_hosts.setdefault('unknown', error)
                        elif 'FATAL:' in line:
                            failed_hosts.setdefault('fatal', True)
                        else:
                            failed_hosts.setdefault('unknown', error)
                except Exception as e:
                    print('%s  %s  %s' % (console_url, time_str, e))
                    continue
                if failed_hosts:
                    print('%s  %s  %s' % (console_url, time_str, ' '.join(sorted(failed_hosts))))
                    if 'unknown' in failed_hosts and failed_hosts['unknown'] != True:
                        print('    %s' % failed_hosts['unknown'])
                    """
                    failed_hosts = sorted(failed_hosts.keys())
                    i = 0
                    while i < len(failed_hosts):
                        print('    %s' % ', '.join(failed_hosts[i:i+12]))
                        i += 12
                    """
            else:
                print('%s  %s' % (console_url, time_str))
        time_end = time.time()
        time_total = int(time_end - time_start)
        print('Time to process %d builds: %d min %d sec' % (num_builds, time_total // 60, time_total % 60))
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get information about Jenkins builds')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    parser.add_argument('-d', '--days', type=int, help='Days in the past to look at (default: %(default)d day(s)) (only valid for --bcs)', default=1)
    parser.add_argument('-s', '--search', help='String to search for in the build logs (only valid for --bcs)', default=None)
    parser.add_argument('-j', '--job', help='Only search a specific job (only valid for --bcs)', default=None)
    parser.add_argument('-b', '--build', help='Only search a specific build (only valid for --bcs)', default=None)
    args = parser.parse_args()
    B = Builds(args)
    if not B.main():
        exit(1)

