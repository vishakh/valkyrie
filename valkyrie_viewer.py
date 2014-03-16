#!/usr/bin/env python2.7

# Reads latest entry from Valkyrie CouchDB instance and displays relevant output as a web page.
# Written by Vishakh.
# https://github.com/vishakh/valkyrie

import json
from mako.template import Template
import os

import couchdb


file_directory = os.path.dirname(os.path.realpath(__file__))
template_file = os.path.join(file_directory, 'valkyrie.mako')
config_file = os.path.join(file_directory, 'config.json')

def readConfigFile(filename):
    json_data = open(filename)
    data = json.load(json_data)
    couchdb_server = data['couchdb_server']
    couchdb_database = data['couchdb_database']
    return couchdb_server, couchdb_database


def fetchDataFromDB():
    couchdb_server, couchdb_database = readConfigFile(config_file)
    server = couchdb.Server(url=couchdb_server)
    db = server[couchdb_database]
    results = db.view('_design/summary/_view/max_unixtime')
    max_unixtime = results.rows[0].value
    doc = db[str(max_unixtime)]
    miners = doc['miners']
    temperature = doc['temperature']
    total_gpus = doc['total_gpus']
    total_hashrate = doc['total_hashrate']
    total_miners = doc['total_miners']
    unixtime = doc['unixtime']
    utctime = doc['utctime']
    return miners, temperature, total_gpus, total_hashrate, total_miners, utctime, unixtime

def index(req):
    miners, temperature, total_gpus, total_hashrate, total_miners, utctime, unixtime = fetchDataFromDB()

    template = Template(filename=template_file)
    return template.render(miners=miners, temperature=temperature, total_gpus=total_gpus, total_hashrate=total_hashrate,
                           total_miners=total_miners, utctime=utctime)