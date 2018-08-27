#!/usr/bin/env python

import sys
import jenkins
import pprint
import json
import traceback
import argparse
import datetime
import time
import subprocess
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen


API_JSON = '/api/json'
CONSOLE_FULL = '/consoleFull'
PRETTY = '?pretty=true'
COMPUTER = '/computer'


class JenkinsInfo(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.username = args.username
        self.password = args.password
        self.days = args.days
        self.search = args.search
        self.job = args.job
        self.build = args.build
        self.cil = args.cil
        self.jn = args.jn
        self.aj = args.aj
        self.bcs = args.bcs
        self.jv = args.jv
        self.cba = args.cba
        self.server = None
        return

    def analyzeLog(self):
        return

    def connect(self):
        url = 'http://%s:%d' % (self.host, self.port)
        try:
            server = jenkins.Jenkins(url, self.username, self.password)
        except Exception as e:
            print('ERROR: could not connect to url %s: %s\n%s' % (url, e, traceback.format_exc(e)))
            server = None
        return server

    def getActiveJobs(self):
        active_jobs = []
        queue = self.server.get_queue_info()
        for entry in queue[:1]:
            data = self.server.get_info(entry['url'])
            for job in data['jobs']:
                if not 'color' in job:
                    continue
                if 'anime' in job['color']:
                    key = [job['url'], job['color'].replace('_anime', '')]
                    if key not in active_jobs:
                        active_jobs.append(key)
        return sorted(active_jobs)

    def getBuilds(self, job_names, days_back, search_for=None):
        s = 'Getting the list of '
        s += 'all ' if not self.job else ('%s ' % self.job)
        s += 'builds in the past %d days' % days_back
        s += '' if not search_for else ('with "%s" in the console output' % search_for)
        print(s)
        builds = []
        num_builds = 0
        time_start = time.time()
        ts = datetime.datetime.now() - datetime.timedelta(days=days_back)
        ts = int(ts.strftime('%s'))
        if self.job:
            job_names = [self.job]
        for i, job_name in enumerate(job_names):
            url = 'http://%s:%d/job/%s%s?tree=allBuilds[url,timestamp]' % (self.host, self.port, job_name, API_JSON)
            try:
                response = urlopen(url, timeout=120)
                data = json.loads(response.read())
                if not 'allBuilds' in data:
                    continue
                use_builds = []
                for build in data['allBuilds']:
                    build_url = build['url']
                    if self.build and not ('/%s/' % self.build) in build_url:
                        continue
                    ts2 = int(build['timestamp']) // 1000
                    if ts2 < ts:
                        break
                    use_builds.append([build_url, ts2])
                print('        %s (%d%%)  (%d of %d)' % (job_name, (i * 100)/len(job_names), len(use_builds), len(data['allBuilds'])))
                builds.extend(use_builds)
            except Exception as e:
                #print('ERROR 3: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
                continue
        time_end = time.time()
        time_total = int(time_end - time_start)
        print('Time to get the list of %d builds: %d min %d sec' % (len(builds), time_total // 60, time_total % 60))
        return builds

    def getComputers(self):
        url = 'http://%s:%d/computer/api/json?tree=computer[_class,displayName]' % (self.host, self.port)
        try:
            response = urlopen(url, timeout=5)
        except Exception as e:
            print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
            return
        data = json.loads(response.read())
        if not 'computer' in data:
            print('ERROR: No computers found')
            return
        computers = []
        [computers.append(computer['displayName']) for computer in data['computer'] if computer['displayName'] != 'master']
        return computers

    def getComputersByArchOSVersion(self, computers):
        computersByArchOSVersion = {}
        for computer in computers:
            url = 'http://%s:%d/computer/%s/systemInfo' % (self.host, self.port, computer)
            try:
                response = urlopen(url, timeout=5)
                lines = response.readlines()
            except Exception as e:
                computersByArchOSVersion.setdefault('unknown', {})
                computersByArchOSVersion['unknown'].setdefault('unknown', [])
                computersByArchOSVersion['unknown']['unknown'].append(computer)
                continue
            arch = None
            _os = None
            version = None
            for line in lines:
                if 'is offline' in line:
                    arch = 'offline'
                    _os = 'offline'
                    version = ''
                    break
                if 'os.arch' in line:
                    arch = line.split('os.arch', 1)[1].split('</td></tr>', 1)[0].replace('<wbr>', '').split('>')[2]
                if 'os.name' in line:
                    _os = line.split('os.name', 1)[1].split('</td></tr>', 1)[0].replace('<wbr>', '').split('>')[2]
                if 'os.version' in line:
                    version = line.split('os.version', 1)[1].split('</td></tr>', 1)[0].replace('<wbr>', '').split('>')[2]
                if arch and _os and version:
                    break
            computersByArchOSVersion.setdefault(arch, {})
            os_version = '%s %s' % (_os, version)
            computersByArchOSVersion[arch].setdefault(os_version, [])
            computersByArchOSVersion[arch][os_version].append(computer)
        return computersByArchOSVersion

    def getComputersInLabel(self):
        url = 'http://%s:%d%s%s' % (self.host, self.port, COMPUTER, API_JSON)
        try:
            response = urlopen(url, timeout=5)
        except Exception as e:
            print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
            return
        data = json.loads(response.read())
        if not 'computer' in data:
            print('ERROR: No computers found')
            return
        labels = {}
        for computer in data['computer']:
            if 'Slave' not in computer['_class']:
                continue
            if not 'assignedLabels' in computer:
                if not 'displayName' in computer:
                    continue
                labels.setdefault(computer['displayName'], {computer['displayName']: computer['numExecutors']})
            else:
                for assignedLabel in computer['assignedLabels']:
                    d = labels.setdefault(assignedLabel['name'], {})
                    d[computer['displayName']] = computer['numExecutors']
        return labels

    def getJobNames(self):
        job_names = []
        queue = self.server.get_queue_info()
        for entry in queue[:1]:
            data = self.server.get_info(entry['url'])
            for job in data['jobs']:
                job_names.append('%s' % job['name'])
        return sorted(job_names)

    def main(self):
        self.server = self.connect()
        if not self.server:
            return False
        job_names = None
        computers = None
        if self.cil:
            computers_in_label = self.getComputersInLabel()
            self.showComputersInLabel(computers_in_label)
        if self.jn:
            job_names = self.getJobNames()
            self.showJobNames(job_names)
        if self.aj:
            active_jobs = self.getActiveJobs()
            self.showActiveJobs(active_jobs)
        if self.bcs:
            job_names = self.getJobNames() if not job_names else job_names
            builds = self.getBuilds(job_names, self.days, self.search)
            self.showBuilds(builds, self.search)
        if self.jv:
            computers = self.getComputers()
            self.showJavaVersions(computers)
        if self.cba:
            if not computers:
                computers = self.getComputers()
            computers_by_arch = self.getComputersByArchOSVersion(computers)
            self.showComputersByArchOSVersion(computers_by_arch)
        return True

    def nslookup(self, ip):
        host = 'unknown'
        ip = ip.strip()
        try:
            output = subprocess.check_output('nslookup %s | grep name' % ip, shell=True)
            if 'name = ' in output:
                host = output.split('name = ', 1)[1].split('.amd', 1)[0]
        except Exception as e:
            pass
        return host

    def showActiveJobs(self, active_jobs):
        print('\n------------------------')
        print('Active Jobs')
        print('------------------------\n')
        if active_jobs:
            print('\nPrevious Build Status  Job')
            print('---------------------  ----------------------------------')
            for url, color in active_jobs:
                name = url.replace('/', ' ').strip().split(' ')[-1]
                print('%-21s  %s' % (color, name))
        else:
            print('There are no active jobs')
        return

    def showBuilds(self, builds, search_for):
        s = 'All builds' if not self.job else ('%s builds' % self.job)
        s += ' in the last %d days' % self.days
        s += ':' if not search_for else (' with "%s" in the console output:' % search_for)
        print(s)
        time_start = time.time()
        num_builds = len(builds)
        for i, build in enumerate(builds):
            url = build[0]
            ts = build[1]
            time_str = time.strftime('%Y-%m-%d %H:%M:%S %a', time.localtime(ts))
            if search_for:
                console_url = url + 'console'
                failed_hosts = {}
                try:
                    response = urlopen(console_url, timeout=15)
                    lines = response.readlines()
                    error = None
                    for line in lines:
                        line = line.strip()
                        if not error and (': error ' in line or ': fatal error ' in line):
                            error = line.split('</span>', 1)[1]
                        if not search_for in line:
                            if 'FATAL: Remote call on' in line:
                                ip = line.split('to /', 1)[1].split(' ', 1)[0]
                                failed_hosts.setdefault(self.nslookup(ip), True)
                            continue
                        if 'Cannot contact ' in line:
                            failed_hosts.setdefault(line.split('Cannot contact ', 1)[1].split(':', 1)[0], True)
                        elif 'to Channel to ' in line:
                            failed_hosts.setdefault(self.nslookup(line.split('to Channel to /', 1)[1]), True)
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
        time_end = time.time()
        time_total = int(time_end - time_start)
        print('Time to process %d builds: %d min %d sec' % (len(builds), time_total // 60, time_total % 60))
        return

    def showComputersByArchOSVersion(self, computers_by_arch):
        for arch in sorted(computers_by_arch):
            print(arch)
            for _os in sorted(computers_by_arch[arch]):
                print('    %s' % _os)
                computers_by_arch[arch][_os] = sorted(computers_by_arch[arch][_os])
                ll = 0
                for c in computers_by_arch[arch][_os]:
                    ll = len(c) if len(c) > ll else ll
                i = 0
                while i < len(computers_by_arch[arch][_os]):
                    print('        %s' % ' '.join(['%-19s' % x for x in computers_by_arch[arch][_os][i:i+10]]))
                    i += 10
        return

    def showComputersInLabel(self, labels):
        print('\n------------------------')
        print('Computers by label')
        print('------------------------\n')
        for label in sorted(labels):
            print('%s:' % label)
            i = 0
            keys = sorted(labels[label].keys())
            while i < len(keys):
                print('    ' + '%s' % ', '.join(keys[i:i+12]))
                i += 12
        return

    def showJavaVersions(self, computers):
        for computer in computers:
            url = 'http://%s:%d/computer/%s/systemInfo' % (self.host, self.port, computer)
            try:
                response = urlopen(url, timeout=5)
                lines = response.readlines()
            except Exception as e:
                #print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
                print('%-30s error' % computer)
                continue
            version = 'unknown'
            for line in lines:
                if 'is offline' in line:
                    print('%-30s offline' % computer)
                    break
                if 'java.version' in line:
                    version = line.split('java.version', 1)[1].split('</td></tr>', 1)[0].replace('<wbr>', '').split('>')[2]
                    print('%-30s %s' % (computer, version))
                    break
        return

    def showJobNames(self, job_names):
        print('\n------------------------')
        print('List of jobs')
        print('------------------------\n')
        print('    ' + '\n    '.join(job_names))
        return



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get information about Jenkins builds')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    parser.add_argument('-u', '--username', help='Jenkins master login username')
    parser.add_argument('-P', '--password', help='Jenkins master login password')
    parser.add_argument('-d', '--days', type=int, help='Days in the past to look at (default: %(default)d day(s)) (only valid for --bcs)', default=1)
    parser.add_argument('-s', '--search', help='String to search for in the build logs (only valid for --bcs)', default=None)
    parser.add_argument('-j', '--job', help='Only search a specific job (only valid for --bcs)', default=None)
    parser.add_argument('-b', '--build', help='Only search a specific build (only valid for --bcs)', default=None)
    parser.add_argument('--cil', action='store_true', help='Show the current list of computers by label')
    parser.add_argument('--jn', action='store_true', help='Show the current list of Jenkins projects/jobs')
    parser.add_argument('--aj', action='store_true', help='Show the currently active projects/jobs')
    parser.add_argument('--bcs', action='store_true', help='Show builds whose logs contain the string (valid with -d, -s, -j and -b')
    parser.add_argument('--jv', action='store_true', help='Show java version by computer')
    parser.add_argument('--cba', action='store_true', help='Show the current list of computers by arch, OS, and version')
    args = parser.parse_args()
    JI = JenkinsInfo(args)
    if not JI.main():
        exit(1)

