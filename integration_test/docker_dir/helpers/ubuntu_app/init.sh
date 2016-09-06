#!/bin/bash

#-------------------------------------------------------------
# Apache Init
#-------------------------------------------------------------
service apache2 start


#-------------------------------------------------------------
# Cassandra Init
#-------------------------------------------------------------
service cassandra start


#-------------------------------------------------------------
# Memcached Init
#-------------------------------------------------------------
wget https://memcached.org/files/memcached-1.4.31.tar.gz
tar -zxf memcached-1.4.31.tar.gz
cd memcached-1.4.31
./configure && make && sudo make install
memcached -u root -d
cd ..


#-------------------------------------------------------------
# MySQL Init
#-------------------------------------------------------------
service mysql start

# initialize the database and link the database to
# the test user docker
cat /tmp/mysql/init.sql | mysql -u root --password=root


#-------------------------------------------------------------
# Nginx Init
#-------------------------------------------------------------
service nginx start


#-------------------------------------------------------------
# Postgresql Init
#-------------------------------------------------------------
service postgresql start

# initialize the database and link the database to
# the test user docker
su -c "cat /tmp/postgresql/init.sql | psql -a" - postgres


#-------------------------------------------------------------
# Redis Init
#-------------------------------------------------------------
# instructions from redis.io/download
wget http://download.redis.io/releases/redis-3.2.3.tar.gz
tar xzf redis-3.2.3.tar.gz
cd redis-3.2.3
make
./src/redis-server &
cd ..


#-------------------------------------------------------------
# Zookeeper Init
#-------------------------------------------------------------
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
