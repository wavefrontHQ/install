#!/bin/bash

# instructions from redis.io/download
wget http://download.redis.io/releases/redis-3.2.3.tar.gz
tar xzf redis-3.2.3.tar.gz
cd redis-3.2.3
make

cd src
./redis-server &

