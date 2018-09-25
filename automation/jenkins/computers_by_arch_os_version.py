#!/usr/bin/env python

import json
import argparse
from utils import getComputers, getComputersByArchOSVersion


class ComputersByArchOSVersion(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        return

    def import_from_file(self):
        computers_by_arch_os_version = {}
        try:
            with open('computers_by_arch_os_version.json') as f:
                computers_by_arch_os_version = json.loads(f.read())
        except Exception as e:
            pass
        return computers_by_arch_os_version

    def main(self):
        imported_computers_by_arch_os_version = self.import_from_file()
        imported_computers_by_name_arch_os_version = self.getComputersByNameArchOSVersion(imported_computers_by_arch_os_version)
        url = 'http://%s:%d' % (self.host, self.port)
        computers = getComputers(url)
        computers_by_arch_os_version = getComputersByArchOSVersion(url, computers)
        computers_by_name_arch_os_version = self.getComputersByNameArchOSVersion(computers_by_arch_os_version)
        computers_by_arch_os_version = self.getUnifiedComputersByArchOSVersion(imported_computers_by_name_arch_os_version, computers_by_name_arch_os_version)
        self.showComputersByArchOSVersion(computers_by_arch_os_version)
        return True

    def getComputersByNameArchOSVersion(self, computers_by_arch_os_version):
        computers_by_name_arch_os_version = {}
        for arch in sorted(computers_by_arch_os_version):
            for os_version in sorted(computers_by_arch_os_version[arch]):
                for computer in computers_by_arch_os_version[arch][os_version]:
                    computers_by_name_arch_os_version.setdefault(computer, {'arch': arch, 'os_version': os_version})
        return computers_by_name_arch_os_version

    def getUnifiedComputersByArchOSVersion(self, imported_computers_by_name_arch_os_version, computers_by_name_arch_os_version):
        unified_computers_by_arch_os_version = {}
        unified_computers_by_name_arch_os_version = {}
        for name in computers_by_name_arch_os_version:
            arch = computers_by_name_arch_os_version[name]['arch']
            os_version = computers_by_name_arch_os_version[name]['os_version']
            if arch == 'offline':
                if not name in imported_computers_by_name_arch_os_version:
                    unified_computers_by_arch_os_version.setdefault(arch, {}).setdefault(os_version, [])
                    if not name in unified_computers_by_arch_os_version[arch][os_version]:
                        unified_computers_by_arch_os_version[arch][os_version].append(name)
                else:
                    imported_arch = imported_computers_by_name_arch_os_version[name]['arch']
                    imported_os_version = imported_computers_by_name_arch_os_version[name]['os_version']
                    if imported_arch != 'offline':
                        unified_computers_by_arch_os_version.setdefault(imported_arch, {}).setdefault(imported_os_version, [])
                        if not name in unified_computers_by_arch_os_version[imported_arch][imported_os_version]:
                            unified_computers_by_arch_os_version[imported_arch][imported_os_version].append(name)
                    else:
                        unified_computers_by_arch_os_version.setdefault(arch, {}).setdefault(os_version, [])
                        if not name in unified_computers_by_arch_os_version[arch][os_version]:
                            unified_computers_by_arch_os_version[arch][os_version].append(name)
            elif name not in imported_computers_by_name_arch_os_version:
                unified_computers_by_arch_os_version.setdefault(arch, {}).setdefault(os_version, [])
                if not name in unified_computers_by_arch_os_version[arch][os_version]:
                    unified_computers_by_arch_os_version[arch][os_version].append(name)
            else:
                unified_computers_by_arch_os_version.setdefault(arch, {}).setdefault(os_version, [])
                if not name in unified_computers_by_arch_os_version[arch][os_version]:
                    unified_computers_by_arch_os_version[arch][os_version].append(name)
        for name in imported_computers_by_name_arch_os_version:
            if name not in computers_by_name_arch_os_version:
                imported_arch = imported_computers_by_name_arch_os_version[name]['arch']
                imported_os_version = imported_computers_by_name_arch_os_version[name]['os_version']
                if not name in unified_computers_by_arch_os_version[imported_arch][imported_os_version]:
                    unified_computers_by_arch_os_version[imported_arch][imported_os_version].append(name)
        return unified_computers_by_arch_os_version

    def showComputersByArchOSVersion(self, computers_by_arch_os_version):
        for arch in sorted(computers_by_arch_os_version):
            print(arch)
            for os_version in sorted(computers_by_arch_os_version[arch]):
                print('    %s' % os_version)
                computers_by_arch_os_version[arch][os_version] = sorted(computers_by_arch_os_version[arch][os_version])
                ll = 0
                for c in sorted(computers_by_arch_os_version[arch][os_version]):
                    ll = len(c) if len(c) > ll else ll
                i = 0
                while i < len(computers_by_arch_os_version[arch][os_version]):
                    print('        %s' % ' '.join(['%-19s' % x for x in computers_by_arch_os_version[arch][os_version][i:i+10]]))
                    i += 10
        with open('computers_by_arch_os_version.json', 'w') as f:
            f.write(json.dumps(computers_by_arch_os_version, sort_keys=True, indent=4))
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get computers by arch, os, version')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    CBAO = ComputersByArchOSVersion(args)
    if not CBAO.main():
        exit(1)

