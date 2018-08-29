#!/usr/bin/env python

import argparse
from utils import getJobNames


class Projects(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        return

    def main(self):
        job_names = getJobNames(self.host, self.port)
        self.showJobNames(job_names)
        return True

    def showJobNames(self, job_names):
        print('\n'.join(sorted(job_names)))
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get list of Jenkins master project/job names')
    parser.add_argument('-H', '--host', help='Jenkins master host name')
    parser.add_argument('-p', '--port', type=int, help='Jenkins master port')
    args = parser.parse_args()
    P = Projects(args)
    if not P.main():
        exit(1)

