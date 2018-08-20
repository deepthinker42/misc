#!/usr/bin/env python

import jenkins
import pprint
import json
import traceback
import argparse


class JenkinsInfo(object):

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.server = None
        return

    def connect(self):
        url = 'http://%s:%d' % (self.host, self.port)
        try:
            server = jenkins.Jenkins(url, self.username, self.password)
        except Exception as e:
            print('ERROR: could not connect to url %s: %s\n%s' % (url, e, traceback.format_exc(e)))
            server = None
        return server

    def main(self):
        self.server = self.connect()
        if not self.server:
            return False
        self.showBuildsInQueue()
        return True

    def showBuildsInQueue(self):
        buildsInQueue = []
        queue = self.server.get_queue_info()
        for entry in queue[:1]:
            data = self.server.get_info(entry['url'])
            for job in data['jobs']:
                if not 'color' in job:
                    continue
                if 'anime' in job['color']:
                    buildsInQueue.append('%s: %s' % (job['url'], job['color']))
                    #print(json.dumps(self.server.get_info(job['url'])))
        if buildsInQueue:
            print('\n'.join(sorted(buildsInQueue)))
        else:
            print('The build queue is empty')
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
