#!/usr/bin/env python3

import testUtils

import argparse
import subprocess
import tempfile
import os

###############################################################
# distributed-transactions-remote-test
#  Tests remote capability of the distributed-transactions-test. Test will setup cluster and pass nodes info to distributed-transactions-test. E.g.
#  distributed-transactions-remote-test.py -v --clean-run --dump-error-detail
###############################################################

Print=testUtils.Utils.Print

def errorExit(msg="", errorCode=1):
    Print("ERROR:", msg)
    exit(errorCode)

pnodes=1
# nodesFile="tests/sample-cluster-map.json"
parser = argparse.ArgumentParser()
parser.add_argument("-p", type=int, help="producing nodes count", default=pnodes)
parser.add_argument("-v", help="verbose", action='store_true')
parser.add_argument("--leave-running", help="Leave cluster running after test finishes", action='store_true')
parser.add_argument("--dump-error-details",
                    help="Upon error print etc/aacio/node_*/config.ini and var/lib/node_*/stderr.log to stdout",
                    action='store_true')
parser.add_argument("--clean-run", help="Kill all nodaac and klaac instances", action='store_true')

args = parser.parse_args()
pnodes=args.p
# nodesFile=args.nodes_file
debug=args.v
dontKill=args.leave_running
dumpErrorDetails=args.dump_error_details
killAll=args.clean_run

testUtils.Utils.Debug=debug

killAacInstances=not dontKill
topo="mesh"
delay=1
prodCount=1 # producers per producer node
total_nodes=pnodes+3
actualTest="tests/distributed-transactions-test.py"
testSuccessful=False

clusterMapJsonTemplate="""{
    "keys": {
        "defproduceraPrivateKey": "%s",
        "defproducerbPrivateKey": "%s"
    },
    "nodes": [
        {"port": 8888, "host": "localhost"},
        {"port": 8889, "host": "localhost"},
        {"port": 8890, "host": "localhost"}
    ]
}
"""

cluster=testUtils.Cluster()

(fd, nodesFile) = tempfile.mkstemp()
try:
    Print("BEGIN")
    cluster.killall(allInstances=killAll)
    cluster.cleanup()

    Print ("producing nodes: %s, non-producing nodes: %d, topology: %s, delay between nodes launch(seconds): %d" %
           (pnodes, total_nodes-pnodes, topo, delay))
    Print("Stand up cluster")
    if cluster.launch(pnodes, total_nodes, prodCount, topo, delay) is False:
        errorExit("Failed to stand up aac cluster.")

    Print ("Wait for Cluster stabilization")
    # wait for cluster to start producing blocks
    if not cluster.waitOnClusterBlockNumSync(3):
        errorExit("Cluster never stabilized")

    producerKeys=testUtils.Cluster.parseClusterKeys(total_nodes)
    defproduceraPrvtKey=producerKeys["defproducera"]["private"]
    defproducerbPrvtKey=producerKeys["defproducerb"]["private"]

    clusterMapJson = clusterMapJsonTemplate % (defproduceraPrvtKey, defproducerbPrvtKey)

    tfile = os.fdopen(fd, "w")
    tfile.write(clusterMapJson)
    tfile.close()

    cmd="%s --nodes-file %s %s %s" % (actualTest, nodesFile, "-v" if debug else "", "--dont-kill" if dontKill else "")
    Print("Starting up distributed transactions test: %s" % (actualTest))
    Print("cmd: %s\n" % (cmd))
    if 0 != subprocess.call(cmd, shell=True):
        errorExit("failed to run cmd.")

    testSuccessful=True
    Print("\nEND")
finally:
    os.remove(nodesFile)
    if not testSuccessful and dumpErrorDetails:
        cluster.dumpErrorDetails()
        Print("== Errors see above ==")

    if killAacInstances:
        Print("Shut down the cluster and cleanup.")
        cluster.killall(allInstances=killAll)
        cluster.cleanup()

exit(0)
