#!/bin/bash

# Export variables
export VIDEO_DIR=./videos
export ORIGIN_PORT=9001
export SSL_CERT=./cert.pem
export SSL_KEY=./privkey.pem
export REPLICA_PORT_1=9002
export REPLICA_PORT_2=9003
export CONTROLLER_PORT=9004
export CACHE_DIR_1=./videos1
export CACHE_DIR_2=./videos2

# Print variables
echo "VIDEO_DIR = $VIDEO_DIR"
echo "ORIGIN_PORT = $ORIGIN_PORT"
echo "SSL_CERT = $SSL_CERT"
echo "SSL_KEY = $SSL_KEY"
echo "REPLICA_PORT_1 = $REPLICA_PORT_1"
echo "REPLICA_PORT_2 = $REPLICA_PORT_2"
echo "CONTROLLER_PORT = $CONTROLLER_PORT"
echo "CACHE_DIR_1 = $CACHE_DIR_1"
echo "CACHE_DIR_2 = $CACHE_DIR_2"