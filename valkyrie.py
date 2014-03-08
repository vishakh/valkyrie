#!/usr/bin/env python2.7

# Uploads Scrypt mining farm status to CouchDB database for detailed logging.
# Written by Vishakh.
# Based on open source code by etkeh <https://github.com/setkeh>

import couchdb
import datetime
import json
import logging
import socket
import sys
import time

def readHostsFile(filename):
    hosts = []
    json_data = open( filename )
    data = json.load(json_data)
    for name in data:
        info = data[name]
        host = info['host']
        port = info['port']
        hosts.append([host, port, name])
    return hosts

def readConfigFile(filename):
    json_data = open( filename )
    data = json.load(json_data)
    couchdb_server = data['couchdb_server']
    couchdb_database = data['couchdb_database']
    socket_timeout = int(data['socket_timeout'])
    log_interval = int(data['log_interval'])
    return couchdb_server, couchdb_database, socket_timeout, log_interval

def linesplit(socket):
    buffer = socket.recv(4096)
    done = False
    while not done:
        more = socket.recv(4096)
        if not more:
            done = True
        else:
            buffer = buffer + more
    if buffer:
        return buffer


def makerpccall(api_command, api_ip, api_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(socket_timeout)
    s.connect((api_ip, int(api_port)))
    if len(api_command) == 2:
        s.send(json.dumps({"command": api_command[0], "parameter": api_command[1]}))
    else:
        s.send(json.dumps({"command": api_command[0]}))
    resp = linesplit(s)
    resp = resp.replace('\x00', '')
    resp = json.loads(resp)
    s.close()
    return resp

def runIteration():
    log.info('Running iteration')
    utctime = str(datetime.datetime.utcnow())
    unix_time = str(time.time())
    miners = {}
    total_hashrate = 0.0
    total_miners = 0
    total_gpus = 0

    for host, port, name in hosts:
        try:
            log.info('Querying %s at %s:%s' % (name, host, port))

            currenthost = {}

            command = 'summary'
            response = makerpccall([command], host, port)
            summary = response['SUMMARY'][0]
            currenthost[command] = summary

            command = 'config'
            response = makerpccall([command], host, port)
            config = response['CONFIG']
            currenthost[command] = config

            command = 'pools'
            response = makerpccall([command], host, port)
            pools = response['POOLS']
            currenthost[command] = pools

            command = 'devs'
            response = makerpccall([command], host, port)
            devices = response['DEVS']
            currenthost[command] = devices

            command = 'coin'
            response = makerpccall([command], host, port)
            devdetails = response['COIN']
            currenthost[command] = devdetails

            #pprint.pprint(currenthost)
            miners[name] = currenthost

            # Cumulative statistics
            hashrate = summary['MHS 5s']
            total_hashrate += hashrate
            total_miners += 1
            gpus = len(devices)
            total_gpus += gpus
        except:
            log.error("Could not fetch data from host " + name + " at host " + host + " and port " + port)
            e = sys.exc_info()[0]
            log.info(e)
    record = {'_id': unix_time, 'unixtime': unix_time, 'utctime': utctime, 'total_hashrate': total_hashrate,
              'total_miners': total_miners,
              'total_gpus': total_gpus, 'temperature': None, 'miners': miners}
    db[unix_time] = record
    db.commit()
    log.info('Done with iteration.')





log = logging.getLogger('Valkyrie')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(filename)s %(lineno)d - %(levelname)s - %(message)s"))
log.addHandler(handler)

config_file = sys.argv[1]
hosts_file = sys.argv[2]

hosts = readHostsFile(hosts_file)
couchdb_server, couchdb_database, socket_timeout, log_interval = readConfigFile(config_file)

server = couchdb.Server(url=couchdb_server)
db = server[couchdb_database]

while True:
    runIteration()
    log.info('Sleeping for %s seconds.'%log_interval)
    time.sleep(log_interval)