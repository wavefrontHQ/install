#!/bin/bash

# install zookeeper
wget http://mirrors.sonic.net/apache/zookeeper/zookeeper-3.4.8/zookeeper-3.4.8.tar.gz
tar -xzf zookeeper-3.4.8.tar.gz
cd zookeeper-3.4.8
echo "tickTime=2000" | sudo tee -a \
       conf/zoo.cfg
echo "dataDir=/var/zookeeper" | sudo tee -a \
       conf/zoo.cfg
echo "clientPort=2181" | sudo tee -a \
       conf/zoo.cfg
./bin/zkServer.sh start &

cd ..
