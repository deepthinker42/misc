#!/usr/bin/env python

import argparse
from utils import getComputersByLabel


class ComputersByLabel(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        return

    def main(self):
        computers_by_label = getComputersByLabel(self.host, self.port)
        self.showComputersInLabel(computers_by_label)
        return True

    def showComputersInLabel(self, labels):
        for label in sorted(labels):
            print('%s:' % label)
            i = 0
            keys = sorted(labels[label].keys())
            while i < len(keys):
                print('    ' + '%s' % ', '.join(keys[i:i+12]))
                i += 12
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get list of Jenkins computers by label')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    CBL = ComputersByLabel(args)
    if not CBL.main():
        exit(1)

