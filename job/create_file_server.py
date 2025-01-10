# -*- coding: utf-8 -*-

import sys
import argparse
from aws.ec2_manager import ec2_manager
import dutil

if __name__ == "__main__":

    dutil.debug_level = 0

    parser = argparse.ArgumentParser(description='craete nfs server @aws.')
    parser.add_argument('-s','--size',type=int,required=True,help='storage size (GB). at least 500GB.')
    parser.add_argument('-sn','--serverName',type=str,required=True,help='server Name tag.')
    parser.add_argument('-it', '--instanceType', type=str, required=True,help='instance type.')
    parser.add_argument('-an', '--amiName', type=str, required=True,help='server ami Name tag.')
    parser.add_argument('-sp', '--snapName', type=str, required=True,help='server snapshot Name tag.')
    parser.add_argument('-st', '--storageType', type=str, required=False,help='server storage type. gp2 or st1. default = st1.')

    args = parser.parse_args()
    size = args.size
    serverName = args.serverName
    instanceType = args.instanceType
    amiName = args.amiName
    snapName = args.snapName
    storageType = args.storageType

    if not storageType:
        storageType='st1'

    server = ec2_manager()
    server.createFileServer(size=size, serverName=serverName, instance_type=instanceType, ami_Name=amiName,
                            snap_Name=snapName, storage_type=storageType)

    sys.exit(0)
