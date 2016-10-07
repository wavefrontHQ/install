#!/bin/bash

SRC_URL="https://raw.githubusercontent.com/kentwang929/install/WF-PCInstallerTest2/install.sh"
SUDO="" # enable "sudo " in unix system
IMAGE=""

if [ "$(uname)" == "Darwin" ]; then
    SUDO=""
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    SUDO="sudo "
fi


# check if base image is built
function check_debian_base() {
  # debian system
  if [ "$(${SUDO}docker images -q ubuntu:itest 2> /dev/null)" == "" ]; then
      echo "Please build base ubuntu images first"
      exit 1
  fi
}


function check_redhat_base() {
  # redhat system
  if [ "$(${SUDO}docker images -q centos:itest 2> /dev/null)" == "" ]; then
      echo "Please build base centos images first"
      exit 1
  fi
}


#-------------------------------------------------------------
# Apache Test
#-------------------------------------------------------------
function test_apache_debian() {
    check_debian_base

    # apache test
    # build apache env
    ${SUDO}docker build -t "apache:test" -f docker_dir/ApacheDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "apache:test" \
            bash -c "service apache2 start && ./test.sh --src_url ${SRC_URL} --keymetric apache.docker_test"

    if [ $? -ne 0 ]; then
        echo "Apache failed"
    else
        echo "Apache succeeded"
    fi
}


function test_apache_redhat() {
    check_redhat_base

    # apache test
    # build apache env
    ${SUDO}docker build -t "apache:rtest" -f docker_dir/ApacheRedhatDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "apache:rtest" \
            bash -c "service httpd start && ./test.sh --src_url ${SRC_URL} --keymetric apache.docker_test"

    if [ $? -ne 0 ]; then
        echo "Apache failed"
    else
        echo "Apache succeeded"
    fi
}


#-------------------------------------------------------------
# Cassandra Test
#-------------------------------------------------------------
function test_cassandra_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "cassandra:test" -f docker_dir/CassandraDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "cassandra:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric GenericJMX.cassandra"

    if [ $? -ne 0 ]; then
        echo "cassandra failed"
    else
        echo "cassandra succeeded"
    fi
}


#-------------------------------------------------------------
# memcached Test
#-------------------------------------------------------------
function test_memcached_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "memcached:test" -f docker_dir/MemcachedDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "memcached:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric memcached."

    if [ $? -ne 0 ]; then
        echo "memcached failed"
    else
        echo "memcached succeeded"
    fi
}


#-------------------------------------------------------------
# MySQL Test
#-------------------------------------------------------------
function test_mysql_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "mysql:test" -f docker_dir/MysqlDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "mysql:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric mysql.docker_test"

    if [ $? -ne 0 ]; then
        echo "mysql failed"
    else
        echo "mysql succeeded"
    fi
}


#-------------------------------------------------------------
# Nginx Test
#-------------------------------------------------------------
function test_nginx_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "nginx:test" -f docker_dir/NginxDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "nginx:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric nginx." 

    if [ $? -ne 0 ]; then
        echo "nginx failed"
    else
        echo "nginx succeeded"
    fi
}


#-------------------------------------------------------------
# Postgresql Test
#-------------------------------------------------------------
function test_postgresql_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "postgres:test" -f docker_dir/PostgresqlDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "postgres:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric postgresql.docker_test"

    if [ $? -ne 0 ]; then
        echo "Postgresql failed"
    else
        echo "Postgresql succeeded"
    fi
}


#-------------------------------------------------------------
# Redis Test
#-------------------------------------------------------------
function test_redis_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "redis:test" -f docker_dir/RedisDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "redis:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric redis_info.docker_test"

    if [ $? -ne 0 ]; then
        echo "Redis failed"
    else
        echo "Redis succeeded"
    fi
}


#-------------------------------------------------------------
# Zookeeper Test
#-------------------------------------------------------------
function test_zookeeper_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "zookeeper:test" -f docker_dir/ZookeeperDebianDock docker_dir/
    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "zookeeper:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric zookeeper."

    if [ $? -ne 0 ]; then
        echo "zookeeper failed"
    else
        echo "zookeeper succeeded"
    fi
}


#-------------------------------------------------------------
# Debian Collectd Test
#-------------------------------------------------------------
function test_debian() {
    check_debian_base

    # build env
    ${SUDO}docker build -t "app:test" -f docker_dir/UbuntuAllDock docker_dir/

    # space separated
    KEYMETRICS="apache.docker_test postgresql.docker_test \
redis_info.docker_test GenericJMX.cassandra \
mysql.docker_test nginx. zookeeper. memcached.docker_test"

    # perform the test
    ${SUDO}docker run -it --cap-add SETPCAP \
            --cap-add SETUID --cap-add SETGID \
            --cap-add DAC_READ_SEARCH \
            "app:test" \
            bash -c "./init.sh && ./test.sh --src_url ${SRC_URL} --keymetric '${KEYMETRICS}'"

    if [ $? -ne 0 ]; then
        echo "Test failed"
    else
        echo "Test succeeded"
    fi
}


function main() {
    # building base ubuntu images
    ${SUDO}docker build -t "ubuntu:itest" -f docker_dir/UbuntuBaseDock docker_dir/
    ${SUDO}docker build -t "centos:itest" -f docker_dir/CentosBaseDock docker_dir/

    ### individual test ###
    # debian test
    # test_apache_debian
    # test_postgresql_debian
    # test_redis_debian
    # test_cassandra_debian
    # test_mysql_debian
    # test_nginx_debian
    # test_zookeeper_debian
    # test_memcached_debian

    # redhat test
    # test_apache_redhat

    test_debian
    echo -e "\nEnd of integration test"
}

main
