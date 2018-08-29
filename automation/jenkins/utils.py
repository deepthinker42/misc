#!/usr/bin/env python

import sys
import jenkins
import json
import traceback
import datetime
import time
import subprocess
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen


def connect(url, username, password):
    try:
        server = jenkins.Jenkins(url, username, password)
    except Exception as e:
        print('ERROR: could not connect to url %s: %s\n%s' % (url, e, traceback.format_exc(e)))
        server = None
    return server

def getActiveJobs(server):
    active_jobs = []
    queue = server.get_queue_info()
    for entry in queue[:1]:
        data = server.get_info(entry['url'])
        for job in data['jobs']:
            if not 'color' in job:
                continue
            if 'anime' in job['color']:
                key = [job['url'], job['color'].replace('_anime', '')]
                if key not in active_jobs:
                    active_jobs.append(key)
    return sorted(active_jobs)

def getBuilds(url, job_names, days_back, search_for=None, specific_job=None, specific_build_number=None):
    s = 'Getting the list of '
    s += 'all ' if not specific_job else ('%s ' % specific_job)
    s += 'builds in the past %d day(s)' % days_back
    s += '' if not search_for else (' with "%s" in the console output' % search_for)
    print(s)
    builds = []
    num_builds = 0
    time_start = time.time()
    ts = datetime.datetime.now() - datetime.timedelta(days=days_back)
    ts = int(ts.strftime('%s'))
    for i, job_name in enumerate(job_names):
        #print(job_name)
        all_builds_url = '%s/job/%s/api/json?tree=allBuilds[url,timestamp]' % (url, job_name)
        try:
            data = json.loads(urlopen(all_builds_url, timeout=120).read())
            if not 'allBuilds' in data:
                continue
            use_builds = []
            for build in data['allBuilds']:
                build_url = build['url']
                if specific_build_number and not ('/%s/' % specific_build_number) in build_url:
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
    print('%s: %d min %d sec' % (s.replace('Getting', 'Time to get'), time_total // 60, time_total % 60))
    return builds

def getComputers(url):
    url = '%s/computer/api/json?tree=computer[_class,displayName]' % url
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
    return sorted(computers)

def getComputersByArchOSVersion(url, computers):
    computersByArchOSVersion = {}
    computers = getComputers(url)
    for computer in computers:
        sysinfo_url = '%s/computer/%s/systemInfo' % (url, computer)
        try:
            response = urlopen(sysinfo_url, timeout=5)
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
    return sorted(computersByArchOSVersion)

def getComputersByLabel(host, port):
    url = 'http://%s:%d/computer/api/json' % (host, port)
    try:
        response = urlopen(url, timeout=5)
    except Exception as e:
        print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
        return
    data = json.loads(response.read())
    if not 'computer' in data:
        print('ERROR: No computers found')
        return
    computers_by_label = {}
    for computer in data['computer']:
        if 'Slave' not in computer['_class']:
            continue
        if not 'assignedLabels' in computer:
            if not 'displayName' in computer:
                continue
            computers_by_label.setdefault(computer['displayName'], {computer['displayName']: computer['numExecutors']})
        else:
            for assignedLabel in computer['assignedLabels']:
                d = computers_by_label.setdefault(assignedLabel['name'], {})
                d[computer['displayName']] = computer['numExecutors']
    return computers_by_label

def getJobNames(server):
    job_names = []
    queue = server.get_queue_info()
    for entry in queue[:1]:
        data = server.get_info(entry['url'])
        for job in data['jobs']:
            job_names.append('%s' % job['name'])
    return sorted(job_names)

def nslookup(ip):
    host = 'unknown'
    ip = ip.strip()
    try:
        output = subprocess.check_output('nslookup %s | grep name' % ip, shell=True)
        if 'name = ' in output:
            host = output.split('name = ', 1)[1].split('.amd', 1)[0]
    except Exception as e:
        pass
    return host

