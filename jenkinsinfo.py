#!/usr/bin/env python

import sys
import jenkins
import pprint
import json
import traceback
import argparse
import datetime
import time
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
        if search_for:
            print('Getting the list of builds in the past %d days with "%s" in the console output.  This will take a while.' % (days_back, search_for))
        else:
            print('Getting the list of builds in the past %d days.  This will take a while.' % days_back)
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
        job_names = self.getJobNames()
        computers_in_label = self.getComputersInLabel()
        active_jobs = self.getActiveJobs()
        """
        self.showJobNames(job_names)
        self.showComputersInLabel(computers_in_label)
        self.showActiveJobs(active_jobs)
        """
        builds = self.getBuilds(job_names, self.days)
        self.processBuilds(builds, self.search)
        self.showBuilds(builds, self.days, self.search)
        return True

    def processBuilds(self, builds, search_for):
        time_start = time.time()
        num_builds = len(builds)
        for i, build in enumerate(builds):
            url = build[0]
            ts = build[1]
            if search_for:
                console_url = url + 'console'
                print('%s (%d%%)' % (console_url, (i * 100) / num_builds))
                failed_hosts = []
                try:
                    response = urlopen(url, timeout=15)
                    lines = response.readlines()
                    for line in lines:
                        if not search_for in line:
                            continue
                        if 'Cannot contact' in line:
                            failed_hosts.setdefault(line.split('contact ', 1)[1].split(':', 1)[0], True)
                except Exception as e:
                    print('ERROR: could not open "%s": %s\n%s' % (url3, e3, traceback.format_exc(e3)))
                    continue
                if failed_hosts:
                    failed_hosts = sorted(failed_hosts.keys())
                    i = 0
                    while i < len(failed_hosts):
                        print('    %s' % ', '.join(failed_hosts[i:i+12]))
                        i += 12
        time_end = time.time()
        time_total = int(time_end - time_start)
        print('Time to process %d builds: %d min %d sec' % (len(builds), time_total // 60, time_total % 60))
        return

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

    def showBuilds(self, builds, days_back, search_for=None):
        if search_for:
            print('Builds in the last %d days with "%s" in the console output:' % (days_back, search_for))
        else:
            print('Builds in the last %d days:' % days_back)
        for url in builds:
            print(url)
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
    parser.add_argument('-d', '--days', type=int, help='Days in the past to look at (default: %(default)d day(s))', default=1)
    parser.add_argument('-s', '--search', help='String to search for in the build logs', default=None)
    parser.add_argument('-j', '--job', help='Only search a specific job', default=None)
    parser.add_argument('-b', '--build', help='Only search a specific build', default=None)
    args = parser.parse_args()
    JI = JenkinsInfo(args)
    if not JI.main():
        exit(1)

