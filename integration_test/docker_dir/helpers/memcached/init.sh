#!/bin/bash
wget https://memcached.org/files/memcached-1.4.31.tar.gz
tar -zxf memcached-1.4.31.tar.gz
cd memcached-1.4.31
./configure && make && sudo make install
memcached -u root -d
cd ..
