#!/usr/bin/python
# coding: UTF-8

import sys
import os
import distutils
import argparse
import dutil

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='copy tree structure.')
    parser.add_argument('-s', '--src', type=str, required=True, help='copy source.')
    parser.add_argument('-d', '--dst', type=str, required=True,help='copy destination.')

    args = parser.parse_args()
    src = args.src
    dst = args.dst

    dutil.logInfo('start copy tree')
    dutil.logInfo(src + " -> " + dst)
    output = distutils.dir_util.copy_tree(src, dst)
    dutil.logInfo(output)

    sys.exit(0)


