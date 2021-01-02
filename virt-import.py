#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime


class VirtImport(object):

    def __init__(self, args):
        self.args = args
        return

    def main(self):
        try:
            cmd = f'virt-install --connect qemu:///system -n {self.args.name} -r {self.args.mem} --os-type={self.args.type} --os-variant={self.args.variant} --disk path={self.args.disk},device=disk,format={self.args.disk.rsplit(".", 1)[1]} --vcpus={self.args.cpus} --vnc --noautoconsole --import'
            os.system(cmd)
            print('\nVM imported.  Open Virtual Machine Manager.')
        except Exception as e:
            print(f'ERROR: could not import vm: {e}')
        return


if __name__ == '__main__':
    today = datetime.today()
    parser = argparse.ArgumentParser('Import qemu/kvm vm')
    parser.add_argument('-n', '--name', help='Name to give imported VM (default: %(default)s)', default=f'{today.strftime("vm-%Y%m%d%H%M%S")}')
    parser.add_argument('-m', '--mem', help='Amount of memory in MB to assign to this VM (default: %(default)s)', default=8192)
    parser.add_argument('-t', '--type', help='Generic type of VM (linux, windows, etc) (default: %(default)s)', default='windows')
    parser.add_argument('-v', '--variant', help='Variant of type of VM (rhel8, centos7, generic) (default: %(default)s)', default='generic')
    parser.add_argument('-d', '--disk', help='Disk file of this VM', required=True)
    parser.add_argument('-c', '--cpus', help='Number of CPUs to assign to this VM (default: %(default)s)', default=4)
    args = parser.parse_args()
    if not os.path.exists(args.disk):
        print(f'ERROR:  "{args.disk}" does not exist')
        exit(1)
    vi = VirtImport(args)
    vi.main()

