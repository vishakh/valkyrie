How to run the program:

valkyrie.py [config file] [hosts file]
e.g. valkyrie.py config.json hosts.json

========== Config Files =========
Sample config file:

{
    "couchdb_server":   "http://user:password@localhost:5984/",
    "couchdb_database": "valkyrie",
    "socket_timeout":   "30",
    "log_interval":     "300"
}

Variables:

couchdb_server      CouchDB server to connect to.
couchdb_database    CouchDB database for recording data.
socket_timeout      Miner socket timeout in seconds.
log_interval        Interval in seconds between logging iterations.

========== Hosts Files =========
Sample hosts file:

{
    "miner1": {"host": "192.168.0.4", "port": "1337"}
}