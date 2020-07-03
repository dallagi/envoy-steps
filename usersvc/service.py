#!/usr/bin/env python

import socket

from flask import Flask, jsonify

app = Flask(__name__)

def enrich_response(response):
    hostname = socket.gethostname()
    resolved = socket.gethostbyname(socket.gethostname())

    return jsonify({ 'hostname': hostname, 'resolved': resolved, **response})


@app.route('/user/health')
def hello():
    my_host_name = socket.gethostname()
    my_resolved_name = socket.gethostbyname(socket.gethostname())

    return enrich_response({'msg': 'Hello World!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

