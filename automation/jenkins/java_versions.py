#!/usr/bin/env python

import sys
import argparse
if sys.version >= (3,):
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
else:
    from urllib2 import Request, urlopen
from utils import getComputers


class JavaVersions(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        return

    def main(self):
        url = 'http://%s:%d' % (self.host, self.port)
        computers = getComputers(url)
        self.showJavaVersions(computers)
        return True

    def showJavaVersions(self, computers):
        computers_by_java_version = {}
        for computer in computers:
            url = 'http://%s:%d/computer/%s/systemInfo' % (self.host, self.port, computer)
            try:
                response = urlopen(url, timeout=5)
                lines = response.readlines()
            except Exception as e:
                #print('ERROR: could not open "%s": %s\n%s' % (url, e, traceback.format_exc(e)))
                computers_by_java_version.setdefault('error', []).append(computer)
                #print('%-30s error' % computer)
                continue
            version = 'unknown'
            for line in lines:
                if 'is offline' in line:
                    computers_by_java_version.setdefault('offline', []).append(computer)
                    #print('%-30s offline' % computer)
                    break
                if 'java.version' in line:
                    version = line.split('java.version', 1)[1].split('</td></tr>', 1)[0].replace('<wbr>', '').split('>')[2]
                    computers_by_java_version.setdefault(version, []).append(computer)
                    #print('%-30s %s' % (computer, version))
                    break
        for version, computers in sorted(computers_by_java_version.items()):
            print(version)
            computers = sorted(computers)
            i = 0
            while i < len(computers):
                print('    %s' % ', '.join(computers[i:i+12]))
                i += 12
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Java versions of Jenkins slaves')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    JV = JavaVersions(args)
    if not JV.main():
        exit(1)

