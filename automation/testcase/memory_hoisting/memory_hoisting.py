#!/usr/bin/env python

import os
import sys
import argparse
import subprocess


NINE_FFFF = 0x9ffff
A0000 = 0xa0000
FFFFF = 0xfffff
ONE_MB = 0x100000
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
                """
                cmd = 'ssh %s@%s free -gt > %s' % (self.username, self.sut, free_out)
                subprocess.call(cmd, shell=True)
                """
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
        if not os.path.exists(self.dmesg_file):
            print('Error: "%s" does not exist' % self.dmesg_file)
            return False
        """
        if not os.path.exists(self.free_file):
            print('Error: "%s" does not exist' % self.free_file)
            return False

        with open(self.free_file) as f:
            free_lines = f.readlines()
        """
        with open(self.dmesg_file) as f:
            dmesg_lines = f.readlines()
        """
        self.test_free(free_lines)
        """
        self.test_bios_e820(dmesg_lines)
        self.test_srat_node(dmesg_lines)
        return True

    def process_dmesg(self):
        return

    def test_free(self, lines):
        free_total_memory = 0
        for line in lines:
            if 'Mem:' in line:
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
            if '[mem' in line:
                starting, ending, label = line.strip().split('[mem ')[1].replace('-', ' ').replace(']', '').split(' ', 2)
            else:
                starting, ending, label = line.strip().split('e820: ')[1].replace('-', ' ').split(' ', 2)
                label = label.replace('(', '').replace(')', '').strip()
            starting = int(starting, 16)
            ending = int(ending, 16)
            self.bios_e820_addr_dict.setdefault(label, {}).setdefault(starting, ending)
            self.bios_e820_addr_list.extend([starting, ending])
        self.bios_e820_addr_list = sorted(self.bios_e820_addr_list)

        """
        if not self.test_bios_e820_contiguous():
            return False
        """
        if not self.test_bios_e820_0_to_9ffff_usable():
            return False
        if not self.test_bios_e820_a0000_to_fffff_reserved():
            return False
        if not self.test_bios_e820_100000_to_100000000_usable():
            return False
        return True

    def test_bios_e820_contiguous(self):
        for i in list(range(2, len(self.bios_e820_addr_list), 2)):
            if self.bios_e820_addr_list[i] - 1 != self.bios_e820_addr_list[i - 1]:
                print('FAIL:  BIOS-e820:  addresses are not contiguous: 0x%x, 0x%x' % (self.bios_e820_addr_list[i - 1], self.bios_e820_addr_list[i]))
                return False
        print('PASS:  BIOS-e820:  addresses are contiguous')
        return True

    def test_bios_e820_0_to_9ffff_usable(self):
        if not 0 in self.bios_e820_addr_dict['usable'] or self.bios_e820_addr_dict['usable'][0] != NINE_FFFF:
            print('FAIL:  BIOS-e820:  address range 0x0 - 0x9ffff is not usable')
            return False
        print('PASS:  BIOS-e820:  address range 0x0 - 0x9ffff is usable')
        return True

    def test_bios_e820_a0000_to_fffff_reserved(self):
        if not A0000 in self.bios_e820_addr_dict['reserved'] or self.bios_e820_addr_dict['reserved'][A0000] != FFFFF:
            print('FAIL:  BIOS-e820:  address range 0xa0000 - 0xfffff is not reserved')
            return False
        print('PASS:  BIOS-e820:  address range 0xa0000 - 0xfffff is reserved')
        return True

    def test_bios_e820_100000_to_100000000_usable(self):
        if not ONE_MB in self.bios_e820_addr_dict['usable']:
            print('FAIL:  BIOS-e820:  address range starting with 0x100000 is not usable')
            return False
        print('PASS:  BIOS-e820:  address range starting with 0x100000 is usable')
        return True

    def test_bios_e820_4GB_usable(self):
        if not FOUR_GB in self.bios_e820_addr_dict['usable']:
            print('FAIL:  BIOS-e820:  address range starting with 0x100000000 is not usable')
            return False
        print('PASS:  BIOS-e820:  address range starting with 0x100000000 is usable')
        return True

    def test_srat_node(self, lines):
        addr_list = []
        addr_dict = {}
        for line in lines:
            if not 'SRAT: Node ' in line:
                continue
            cols = line.strip().split()[-1].replace(']', '').split('-')
            starting = long(cols[0], 16)
            ending = long(cols[1], 16)
            addr_list.extend([starting, ending])
            addr_dict[starting] = ending

        if not self.test_srat_node_0_to_under_4GB_contiguous(addr_dict):
            return False
        if not self.test_srat_node_memory_hole_under_4GB_hoisted_to_4GB(addr_dict):
            return False
        if not self.test_srat_node_memory_hole_under_1TB_hoisted_to_1TB(addr_list, addr_dict):
            return False
        return True

    def test_srat_node_0_to_under_4GB_contiguous(self, addr_dict):
        starting_addr_indices = list(range(2, len(self.bios_e820_addr_list), 2))
        for starting_addr in starting_addr_indices:
            if (self.bios_e820_addr_list[starting_addr] != self.bios_e820_addr_list[starting_addr - 1] + 1) and self.bios_e820_addr_list[starting_addr] < addr_dict[0]:
                print('FAIL:  SRAT:  address ranges between 0 and 0x100000000 are not contiguous (0x%0x, 0x%0x)' % (self.bios_e820_addr_list[starting_addr - 1], self.bios_e820_addr_list[starting_addr]))
                break
        print('PASS:  SRAT:  address ranges between 0 and 0x100000000 are contiguous')
        return True

    def test_srat_node_memory_hole_under_4GB_hoisted_to_4GB(self, addr_dict):
        hole_size = (FOUR_GB - 1) - (addr_dict[0] + 1)
        if addr_dict[FOUR_GB] < FOUR_GB + hole_size:
            print('FAIL:  SRAT:  0x%x hole starting 0x%x not hoisted above 4GB (0x%x)' % (hole_size, addr_dict[0] + 1, addr_dict[FOUR_GB]))
            return False
        print('PASS:  SRAT:  0x%x hole starting 0x%x hoisted above 4GB (0x%x - 0x%x)' % (hole_size, addr_dict[0] + 1, FOUR_GB, addr_dict[FOUR_GB]))
        return True

    def test_srat_node_memory_hole_under_1TB_hoisted_to_1TB(self, addr_list, addr_dict):
        if not ONE_TB in addr_dict:
            print('PASS:  SRAT:  no hole at 1TB because system has less than 1TB of memory')
            return True
        ending_addr = addr_list[addr_list.index(ONE_TB) - 1]
        hole_size = (ONE_TB - 1) - (ending_addr + 1)
        if addr_dict[ONE_TB] < ONE_TB + hole_size:
            print('FAIL:  SRAT:  0x%x hole starting 0x%x not hoisted above 1TB (0x%x)' % (hole_size, ending_addr + 1, addr_dict[ONE_TB]))
            return False
        print('PASS:  SRAT:  0x%x hole starting 0x%x hoisted above 1TB (0x%x - 0x%x)' % (hole_size, ending_addr + 1, ONE_TB, addr_dict[ONE_TB]))
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

