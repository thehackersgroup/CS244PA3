#!/usr/bin/python

"CS244 Assignment 3: pFabric"

from time import sleep, time
import termcolor as T
from argparse import ArgumentParser
import socket
import traceback
import struct
import math
import sys
from workload import Workload
import random
from subprocess import Popen

# Parse arguments
parser = ArgumentParser(description="Bufferbloat tests")
parser.add_argument('--src-ip',
                    help="source IP",
                    required=True)

parser.add_argument('--num-bands',
                    help="number of priority bands",
                    type=int,
                    required=True)

parser.add_argument('--packet-size',
                    help="packet size (bytes)",
                    type=int,
                    default=1500)

parser.add_argument('--workload',
                    help="workload distribution file",
                    required=True)

parser.add_argument('--bw',
                    help="bandwidth of link",
                    type=int,
                    default=1000)

parser.add_argument('--load',
                    help="load level (%)",
                    type=float,
                    required=True)

parser.add_argument('--time',
                    help="number of seconds to run",
                    type=int,
                    default=6000)

parser.add_argument('--dest-file',
                    help="file containing info for destinations",
                    required=True)

parser.add_argument('--output-dir',
                    help="output directory",
                    required=True)

# FOR DEBUGGING ONLY
parser.add_argument('--priority',
                    help="set priority for flow",
                    type=int,
                    default=None)

# Expt parameters
args = parser.parse_args()
skt = None

def readReceivers():
    receivers = []
    infile = open(args.dest_file, 'r')
    lines = infile.readlines()
    infile.close()
    for i in xrange(len(lines)/2):
        ip = lines[2*i].split('\n')[0]
        port = int(lines[2*i+1])
        receivers.append((ip, port))
    return receivers

def main():
    "Create flows"
    sys.stdout.flush()

    # Initialize workload
    workload  = Workload(args.workload)
    receivers = readReceivers()
    print "NUM RECEIVERS: %d" % len(receivers)

    flowStartCmd = "sudo python ./flowGenerator.py --src-ip %s --src-port %d --dest-ip %s --dest-port %d --num-packets %d --num-bands %d --max-packets %d --packet-size %d --out %s/send-%s-%d.txt > test.txt"

    #random.seed(1234568)
    print "STARTING AT TIME %f" % time()
    srcPort = 5000
    start = time()
    while time() - start < args.time:
        lambd = args.load * args.bw * 1000000 / 8 / args.packet_size / workload.getAverageFlowSize()
        waitTime = random.expovariate(lambd)
        print "Sleeping for %f seconds..." % waitTime
        sys.stdout.flush()
        sleep(waitTime)

        # get random receiver
        i = random.randrange(len(receivers))
        (dest_ip, dest_port) = receivers[i]
        numPackets = workload.getFlowSize()

        print "Sending %d packets from %s:%d to %s:%d" % (numPackets, args.src_ip, srcPort, dest_ip, dest_port)
        Popen(flowStartCmd % (args.src_ip, srcPort, dest_ip, dest_port, numPackets, args.num_bands, 
                              workload.getMaxFlowSize(), args.packet_size, args.output_dir, args.src_ip, srcPort), shell=True)
        srcPort += 1

    print "ENDING AT TIME %f" % time()

if __name__ == '__main__':
    try:
        main()
    except:
        if skt:
            skt.close()
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        traceback.print_exc(file=sys.stdout)

