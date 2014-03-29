#!/usr/bin/env python2.7

# Uploads Scrypt mining farm status to CouchDB database for detailed logging.
# Written by Vishakh.
# https://github.com/vishakh/valkyrie
# Based on open source code by etkeh <https://github.com/setkeh>

import datetime
import json
import logging
import socket
import subprocess
import sys
import time

import couchdb


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
    temperature_script = None
    if 'temperature_script' in data:
        temperature_script = data['temperature_script']
    return couchdb_server, couchdb_database, socket_timeout, log_interval, temperature_script

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


def tryDBConnect():
    server = couchdb.Server(url=couchdb_server)
    db = server[couchdb_database]
    return db, server


def connectToDB():
    log.info("Connecting to DB.")
    while True:
        try:
            db, server = tryDBConnect()
            log.info("DB connect successful.")
            return server, db
        except:
            e = sys.exc_info()[0]
            log.error("Could not connect to DB.")
            log.info(e)
            log.info("Will retry after sleep..")
            time.sleep(log_interval)


def runIteration():
    log.info('Running iteration')
    try:
        utctime = str(datetime.datetime.utcnow())
        unix_time = str(time.time())
        miners = {}
        total_hashrate = 0.0
        total_miners = 0
        total_gpus = 0
        temperature = None

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

                miners[name] = currenthost

                temperature = None
                try:
                    if temperature_script is not None:
                        temperature = subprocess.check_output(temperature_script).strip()
                        temperature = temperature.replace('\r', '').replace('\n', '')
                    else:
                        log.info('Skipping temperature recording as no script is provided.')
                except:
                    log.warn('Could not get farm temperature.')
                    e = sys.exc_info()[0]
                    log.info(e)

                # Cumulative statistics
                hashrate = summary['MHS 5s']
                if (type(hashrate) == str or type(hashrate) is None) and ('E' in hashrate or 'e' in hashrate):
                    hashrate = float(hashrate[:-1])/10
                total_hashrate += hashrate
                total_miners += 1
                gpus = len(devices)
                total_gpus += gpus
            except:
                log.error("Could not fetch data from host " + name + " at host " + host + " and port " + port)
                e = sys.exc_info()
                log.info(e)
        record = {'_id': unix_time, 'unixtime': unix_time, 'utctime': utctime, 'total_hashrate': total_hashrate,
                  'total_miners': total_miners,
                  'total_gpus': total_gpus, 'temperature': temperature, 'miners': miners}
        try:
            db[unix_time] = record
            db.commit()
        except:
            log.warn('Could not write to database. Attempting to reconnect for next iteration..')
            connectToDB()
    except:
        e = sys.exc_info()
        log.error("Error during iteration")
        logging.exception(e)
    log.info('Done with iteration.')


log = logging.getLogger('Valkyrie')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(filename)s %(lineno)d - %(levelname)s - %(message)s"))
log.addHandler(handler)

config_file = sys.argv[1]
hosts_file = sys.argv[2]

hosts = readHostsFile(hosts_file)
couchdb_server, couchdb_database, socket_timeout, log_interval, temperature_script = readConfigFile(config_file)


server, db = connectToDB()

while True:
    runIteration()
    log.info('Sleeping for %s seconds.'%log_interval)
    time.sleep(log_interval)
