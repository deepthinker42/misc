#!/usr/bin/env python

import os
import sys
import argparse
import subprocess



FOUR_GB = 4 * 1024 * 1024 * 1024
ONE_TB = 1024 * 1024 * 1024 * 1024


class MemoryHoistingTest(object):

    def __init__(self, args):
        self.cpus = args.cpus
        self.dpcs = args.dpcs
        self.num_chips = args.chips
        self.mem_size_in_gb = args.gb
        self.interleave = args.interleave
        self.dmesg_file = args.dmesg
        self.free_file = args.free
        self.username = args.username
        self.sut = args.sut

        self.total_memory = self.num_chips * self.mem_size_in_gb
        self.bios_e820_addr_list = []
        self.bios_e820_addr_dict = {}
        return

    def main(self):
        if self.sut:
            dmesg_out = '%s.dmesg.out' % self.sut
            free_out = '%s.free.out' % self.sut
            try:
                cmd = 'ssh %s@%s dmesg > %s' % (self.username, self.sut, dmesg_out)
                subprocess.call(cmd, shell=True)
                cmd = 'ssh %s@%s free -gt > %s' % (self.username, self.sut, free_out)
                subprocess.call(cmd, shell=True)
            except Exception as e:
                print('Error: command "%s" failed: %s\n%s' % cmd, e, traceback.format_exc(e))
                return False
            if not os.path.exists(dmesg_out):
                print('Error: %s does not exist' % dmesg_out)
                return False
            if not os.path.exists(free_out):
                print('Error: %s does not exist' % free_out)
                return False
            self.dmesg_file = dmesg_out
            self.free_file = free_out
        elif not os.path.exists(self.dmesg_file):
            print('Error: "%s" does not exist' % self.dmesg_file)
            return False
        elif not os.path.exists(self.free_file):
            print('Error: "%s" does not exist' % self.free_file)
            return False

        with open(self.free_file) as f:
            free_lines = f.readlines()
        with open(self.dmesg_file) as f:
            dmesg_lines = f.readlines()
        self.test_free(free_lines)
        self.test_bios_e820(dmesg_lines)
        self.test_srat_node_0_pxm_0(dmesg_lines)
        return True

    def process_dmesg(self):
        return

    def test_free(self, lines):
        free_total_memory = 0
        for line in lines:
            if line.startswith('Mem:'):
                free_total_memory = int(line.split()[1])
                break
        if abs(self.total_memory - free_total_memory) >= 3:
            print('FAIL:  Free memory:  Calculated memory (%dG) does not match free memory (%dG)' % (self.total_memory, free_total_memory))
            return False
        print('PASS:  Free memory:  Calculated memory (%dG) matches free memory (%dG)' % (self.total_memory, free_total_memory))
        return True

    def test_bios_e820(self, lines):
        e820 = {}
        for line in lines:
            if not 'BIOS-e820: ' in line:
                continue
            cols = line.strip().split()
            starting = int(cols[1], 16)
            ending = int(cols[3], 16)
            label = cols[4].strip('(').strip(')')
            self.bios_e820_addr_dict.setdefault(label, {}).setdefault(starting, ending)
            self.bios_e820_addr_list.extend([starting, ending])
        self.bios_e820_addr_list = sorted(self.bios_e820_addr_list)
        for i in list(range(len(self.bios_e820_addr_list) - 1)):
            if self.bios_e820_addr_list[i] > self.bios_e820_addr_list[i+1]:
                print('FAIL:  BIOS-e820:  addresses are not contiguous: %s' % ' '.join([hex(x) for x in self.bios_e820_addr_list]))
                return False
        print('PASS:  BIOS-e820:  addresses are contiguous')
        if self.total_memory > 4:
            found = False
            for k, v in self.bios_e820_addr_dict['reserved'].items():
                if k < FOUR_GB and v <= (FOUR_GB * .95):
                    found = True
            if not found:
                print('FAIL:  BIOS-e820:  no memory range found within 95%% of 4GB')
                return False
            print('PASS:  BIOS-e820:  memory range found within 95% of 4GB')
        return True

    def test_srat_node_0_pxm_0(self, lines):
        addr_list = []
        addr_dict = {}
        for line in lines:
            if not 'SRAT: Node ' in line:
                continue
            cols = line.strip().split()[-1].split('-')
            starting = int(cols[0], 16)
            ending = int(cols[1], 16)
            addr_list.extend([starting, ending])
            addr_dict[starting] = ending
        if not FOUR_GB in addr_dict:
            print('FAIL:  SRAT:  no address range starting at 4GB')
        else:
            print('PASS:  SRAT:  usable address starting at 4GB')
            if not addr_dict[FOUR_GB] == self.bios_e820_addr_dict['usable'][FOUR_GB]:
                print('FAIL:  SRAT:  no matching address range starting at 4GB found in BIOS-e820')
            else:
                print('PASS:  SRAT:  matching address range starting at 4GB found in BIOS-e820')
        if self.total_memory >= 1024:
            if not ONE_TB in addr_dict:
                print('FAIL:  SRAT:  no address range starting at 1TB found')
            else:
                print('PASS:  SRAT:  address range starting at 1TB found')
        else:
            print('PASS:  SRAT:  total memory < 1TB')
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Memory Hoisting Test')
    parser.add_argument('-c', '--cpus', type=int, help='Number of CPUs (default: %(default)d)', choices=[1, 2], default=1)
    parser.add_argument('-d', '--dpcs', type=int, help='Number of DPCs (default: %(default)d)', choices=[1, 2], default=1)
    parser.add_argument('-n', '--chips', type=int, help='Number of memory chips installed (default: %(default)d)', choices=[1, 2, 4, 8, 16, 32], default=2)
    parser.add_argument('-g', '--gb', type=int, help='Size in GB of each memory chip (default: %(default)d)', choices=[4, 8, 16, 32, 64], default=8)
    parser.add_argument('-i', '--interleave', help='Interleave (default: %(default)s)', choices=[None, 'chipset', 'channel'], default=None)
    parser.add_argument('-f', '--dmesg', help='Path to output of dmesg', default='dmesg.out')
    parser.add_argument('-F', '--free', help='Path to output of free', default='free.out')
    parser.add_argument('-u', '--username', help='Username for ssh to SUT', default='srv_bios')
    parser.add_argument('-s', '--sut', help='SUT from which to get dmesg outut')
    args = parser.parse_args()
    MHT = MemoryHoistingTest(args)
    if not MHT.main():
        exit(1)

