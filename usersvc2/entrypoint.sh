#!/bin/sh

pipenv run python /application/service.py & /usr/local/bin/envoy -c /application/envoy.yaml
