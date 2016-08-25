SRC_URL="https://raw.githubusercontent.com/kentwang929/install/WF-PCInstallerTest/install.sh"


# check if base image is built
function check_base() {
  if [ "$(docker images -q ubuntu:itest 2> /dev/null)" == "" ]; then
      echo "Please build base images first"
      exit 1
  fi
}


function test_apache() {
    check_base

    # apache test
    # build apache env
    docker build -t "apache:test" -f docker_dir/ApacheDebianDock docker_dir/
    # perform the test
    docker run -it --cap-add SETPCAP \
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


function main() {
    # building base ubuntu images
    docker build -t "ubuntu:itest" -f docker_dir/UbuntuBaseDock docker_dir/
    test_apache
}

main
