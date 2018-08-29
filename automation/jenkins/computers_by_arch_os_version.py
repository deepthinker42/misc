#!/usr/bin/env python

import argparse
from utils import getComputers, getComputersByArchOSVersion


class ComputersByArchOSVersion(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        return

    def main(self):
        url = 'http://%s:%d' % (self.host, self.port)
        computers = getComputers(url)
        computers_by_arch_os_version = getComputersByArchOSVersion(url, computers)
        self.showComputersByArchOSVersion(computers_by_arch_os_version)
        return True

    def showComputersByArchOSVersion(self, computers_by_arch_os_version):
        for arch in sorted(computers_by_arch_os_version):
            print(arch)
            for _os in sorted(computers_by_arch_os_version[arch]):
                print('    %s' % _os)
                computers_by_arch_os_version[arch][_os] = sorted(computers_by_arch_os_version[arch][_os])
                ll = 0
                for c in computers_by_arch_os_version[arch][_os]:
                    ll = len(c) if len(c) > ll else ll
                i = 0
                while i < len(computers_by_arch_os_version[arch][_os]):
                    print('        %s' % ' '.join(['%-19s' % x for x in computers_by_arch_os_version[arch][_os][i:i+10]]))
                    i += 10
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get computers by arch, os, version')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    CBAO = ComputersByArchOSVersion(args)
    if not CBAO.main():
        exit(1)

