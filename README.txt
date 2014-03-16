============================
========== SERVER ==========
============================

How to run the program:

valkyrie.py [config file] [hosts file]
e.g. valkyrie.py config.json hosts.json

========== Config Files =========
Sample config file:

{
    "couchdb_server":       "http://user:password@localhost:5984/",
    "couchdb_database":     "valkyrie",
    "socket_timeout":       "30",
    "log_interval":         "300"
    "temperature_script":   "/path/to/temperature_test.py"
}

Variables:

couchdb_server      CouchDB server to connect to.
couchdb_database    CouchDB database for recording data.
socket_timeout      Miner socket timeout in seconds.
log_interval        Interval in seconds between logging iterations.
temperature_script  Path to a script that outputs (only) the room temperature.

========== Hosts Files =========
Sample hosts file:

{
    "miner1": {"host": "192.168.0.4", "port": "1337"}
}

========== Running as a service =========

Always run the program manually from the command line first to ensure all dependencies are met.

In Debian-like systems:

1. Copy valkyrie.py to /usr/local/sbin/valkyrie.py
2. Copy valkyrie.init.d.sample to /etc/init.d/valkyrie.
3. Copy config.json and hosts.json as described above to /etc/valkyrie.
4. Run 'sudo update-rc.d valkyrie defaults' to set up the new service.
5. Run 'sudo service valkyrie start' to start the service.
6. Open '/var/log/valkyrie.log' to view the service log.

============================
========== CLIENT ==========
============================

The viewer relies on a CouchDB view called 'max_unixtime' in a design document called 'summary'.

The map and reduce functions are:

function(doc) {
  emit(null, doc.unixtime);
}

function (key, values, rereduce) {
    return Math.max.apply(null, values);
}

Once the above view is set up:
1. Extract repo in the documents folder of a Python-enabled web server.
2. Ensure config.json makes sense. This can be identical to the server config.json.
3. Ensure all Python modules, e.g. json and mako, are installed.
4. Open the URI corresponding to valkyrie_viewer.py in a web browser.