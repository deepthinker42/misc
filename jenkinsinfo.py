#!/usr/bin/env python

import sys
import jenkins
import pprint
import json
import traceback
import argparse
import datetime
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

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
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
        return active_jobs

    def getBuilds(self, job_names, hours_back, text=None):
        if text:
            print('Getting the list of builds in the past %d hours with "%s" in the console output.  This will take 5-10 minutes.' % (hours_back, text))
        else:
            print('Getting the list of builds in the past %d hours.  This will take around 2-5 minutes.' % hours_back)
        builds = []
        ts = datetime.datetime.now() - datetime.timedelta(hours=hours_back)
        ts = int(ts.strftime('%s'))
        for job_name in job_names:
            url = 'http://%s:%d/job/%s%s' % (self.host, self.port, job_name, API_JSON)
            try:
                response = urlopen(url, timeout=5)
                data = json.loads(response.read())
                if not 'builds' in data:
                    continue
                for build in data['builds']:
                    url2 = build['url'] if not build['url'].endswith('/') else build['url'][:-1]
                    url2 += API_JSON
                    try:
                        response2 = urlopen(url2, timeout=5)
                        data2 = json.loads(response2.read())
                        if not 'timestamp' in data2:
                            continue
                        ts2 = int(data2['timestamp']) // 1000
                        if ts2 < ts:
                            break
                        if text:
                            url3 = url2.replace(API_JSON, '/console')
                            try:
                                response3 = urlopen(url3, timeout=5)
                                data3 = response3.read()
                                if not text in data3:
                                    continue
                            except Exception as e3:
                                #print('ERROR: could not open "%s": %s\n%s' % (url3, e3, traceback.format_exc(e3)))
                                #print('ERROR: could not open "%s"' % url3)
                                continue
                            builds.append(url3)
                        else:
                            builds.append(url2)
                    except Exception as e2:
                        #print('ERROR: could not open "%s": %s\n%s' % (url2, e2, traceback.format_exc(e2)))
                        #print('ERROR: could not open "%s"' % url2)
                        continue
            except Exception as e:
                #print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
                #print('ERROR: could not open "%s"' % url)
                continue
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
        return job_names

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
        builds = self.getBuilds(job_names, 24, 'remoting')
        self.showBuilds(builds, 24, 'remoting')
        return True

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

    def showBuilds(self, builds, hours_back, text=None):
        if text:
            print('Builds in the last %d hours with "%s" in the console output:' % (hours_back, text))
        else:
            print('Builds in the last %d hours:' % hours_back)
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
    args = parser.parse_args()
    JI = JenkinsInfo(args.host, args.port, args.username, args.password)
    if not JI.main():
        exit(1)

