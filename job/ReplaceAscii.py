#!/usr/bin/python
# coding: UTF-8

import os
import argparse

def replaceAscii(fileName,keyList):

    filedata = None
    with open(fileName, "r") as file:
        filedata = file.read()

    for key in keyList:
        filedata = filedata.replace(key[0],key[1])

    with open(fileName, "w") as file:
        file.write(filedata)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='replace ascii text.')
    parser.add_argument('-f', '--fileName', type=str, required=True,help='fileName.')
    parser.add_argument('-l', '--list',type=str,required=True, help='list of tapple. eg \'[(\'before\',\'after\')\']')

    args = parser.parse_args()

    fileName = args.fileName
    keyList = eval(args.list)

    replaceAscii(fileName,keyList)
