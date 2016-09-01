#!/bin/bash

SRC_URL="https://raw.githubusercontent.com/kentwang929/install/WF-PCInstallerTest2/install.sh"
SUDO="" # enable "sudo " in Debian
IMAGE=""

# check if base image is built
function check_base() {
  if [ "$(${SUDO}docker images -q ubuntu:itest 2> /dev/null)" == "" ]; then
      echo "Please build base images first"
      exit 1
  fi
}


function test_apache() {
    check_base

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


function test_postgresql() {
    check_base

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


function test_redis() {
    check_base

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


function test_cassandra() {
    check_base

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


function test_mysql() {
    check_base

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



function test_debian() {
    check_base

    # build env
    ${SUDO}docker build -t "app:test" -f docker_dir/UbuntuAllDock docker_dir/

    KEYMETRICS="apache.docker_test postgresql.docker_test \
                redis_info.docker_test GenericJMX.cassandra \
                mysql.docker_test"
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
    # test_apache
    # test_postgresql 
    # test_redis
    # test_cassandra
    # test_mysql
    test_debian
}

main
