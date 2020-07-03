#!/usr/bin/env python

import logging
import os
import pg8000
import socket

from flask import Flask, jsonify, request

pg8000.paramstyle = 'named'

HOSTNAME = socket.gethostname()
RESOLVED_NAME = socket.gethostbyname(socket.gethostname())

logging.basicConfig(
    filename='/tmp/flasklog',
    level=logging.DEBUG,
    format="%(asctime)s esteps-user 0.0.1 %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = Flask(__name__)
logging.info("esteps-user initializing on %s (resolved %s)" % (HOSTNAME, RESOLVED_NAME))


def get_db(database):
    db_host = os.environ.get("USER_DB_RESOURCE_HOST", "postgres")
    db_port = int(os.environ.get("USER_DB_RESOURCE_PORT", 5432))

    return pg8000.connect(user="postgres", password="postgres",
                          database=database, host=db_host, port=db_port)


class DbInitializationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "<DbInitializationError '{}'>".format(self.message)


def initialize_database_if_tables_do_not_exist():
    try:
        conn = get_db("postgres")
        conn.autocommit = True

        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'users'")
        results = cursor.fetchall()

        if not results:
            cursor.execute("CREATE DATABASE users")

        conn.close()
    except pg8000.Error as e:
        raise DbInitializationError("no user database in setup: %s" % e)

    try:
        conn = get_db("users")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                uuid VARCHAR(64) NOT NULL PRIMARY KEY,
                username VARCHAR(64) NOT NULL,
                fullname VARCHAR(2048) NOT NULL,
                password VARCHAR(256) NOT NULL
            )
                ''')
        conn.commit()
        conn.close()
    except pg8000.Error as e:
        raise DbInitializationError("no user table in setup: %s" % e)


def params(request, *required):
    all_params = request.get_json()

    logging.debug("json params: {}".format(all_params))

    missing = [key for key in needed if key not in incoming]

    if missing:
        raise Exception('Required fields missing: {}'.format(missing))
    return all_params


def get_user(_request, username):
    try:
        conn = get_db("users")
        cursor = conn.cursor()

        cursor.execute("SELECT uuid, fullname FROM users WHERE username = :username", locals())
        [ useruuid, fullname ] = cursor.fetchone()

        return dict(uuid=useruuid, fullname=fullname)
    except pg8000.Error as e:
        raise Exception("{}: could not fetch info: {}".format(username, e))


def create_user(request, username):
    try:
        req_params = params(request, 'fullname', 'password')

        logging.debug("handle_user_put {}: got args {}".format(username, req_params))

        fullname = req_params['fullname']
        password = req_params['password']

        useruuid = uuid.uuid4().hex.upper();

        logging.debug("handle_user_put %s: useruuid %s" % (username, useruuid))

        conn = get_db("users")
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users VALUES(:useruuid, :username, :fullname, :password)', locals())
        conn.commit()

        return dict(uuid=useruuid, fullname=fullname)
    except pg8000.Error as e:
        raise Exception("{}: could not save info: {}".format(username, e))


def enrich_response(response):
    return jsonify({ 'hostname': HOSTNAME, 'resolved_name': RESOLVED_NAME, **response})


@app.route('/user/<username>', methods=['POST', 'GET'])
def handle_user(username):
    logging.debug("handle_user %s: method %s" % (username, request.method))

    try:
        initialize_database_if_tables_do_not_exist()

        if rc:
            if request.method == 'POST':
                user = create_user(request, username)
                return enrich_response(user), 201
            else:
                user = get_user(request, username)
                return enrich_response(user), 200
    except Exception as e:
        return enrich_response({'error': str(e)}), 500


@app.route('/user/health')
def health_check():
    return enrich_response({'msg': 'Hello World!'}), 200

if __name__ == '__main__':
    initialize_database_if_tables_do_not_exist()
    app.run(host='0.0.0.0', port=5000, debug=True)

