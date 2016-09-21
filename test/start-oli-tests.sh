

#TARGET_SCRIPT="https://raw.githubusercontent.com/wavefrontHQ/install/telegraf/install.sh"
#INSTANCE="https://try.wavefront.com"
#API_TOKEN="e26080f7-a26b-464b-8a0e-f1f765da6ce0"
#TEST_METRIC="cpu_usage_idle"

TARGET_SCRIPT="$1"
INSTANCE="$2"
API_TOKEN="$3"
TEST_METRIC="$4"

echo $TARGET_SCRIPT
echo $INSTANCE
echo $API_TOKEN
echo $TEST_METRIC

CONTAINERS=("ubuntu1404"
  "centos6"
  "centos7")
IMAGES=("ubuntu:14.04"
  "centos:centos6"
  "centos:centos7")
OLI_SCRIPTS=("debian-one-line-install.sh"
  "rhel-one-line-install.sh"
  "rhel-one-line-install.sh")

echo STARTING OLI TESTS

# Spin up each of the containers and run OLI install on them.
for i in "${!CONTAINERS[@]}"; do
    CONTAINER_NAME="${CONTAINERS[$i]}"
    IMAGE="${IMAGES[$i]}"
    OLI_SCRIPT="${OLI_SCRIPTS[$i]}"
    LOG_FILE="logs/${CONTAINERS[$i]}.log"

    rm -f $LOG_FILE
    docker run -i --sig-proxy=true -e TERM=xterm-color --name=$CONTAINER_NAME -h $CONTAINER_NAME --cap-add ALL -e INSTANCE=$INSTANCE -e API_TOKEN=$API_TOKEN -e TARGET_SCRIPT=$TARGET_SCRIPT -v $(pwd)/scripts:/scripts $IMAGE /bin/bash /scripts/$OLI_SCRIPT >> $LOG_FILE 2>&1 &
    echo $CONTAINER_NAME started, to attach a shell, run "docker exec -it $CONTAINER_NAME /bin/bash"
done

echo "Check the logs directory for out put from each container. To further debug a container, attach to it using the command above."
echo "Waiting 1 minute before querying Wavefront APIs for data."
sleep 60
# Query API continuously
echo "Entering API Query Loop. This will query every 30 seconds. Tests have passed when every container reports SUCCESS."
echo "Press CTRL+C to exit. Run stop-oli-test.sh to shutdown and destroy test containers"
while :
do
  for i in "${!CONTAINERS[@]}"; do
  	python scripts/poll-api.py $INSTANCE $API_TOKEN ${CONTAINERS[$i]} $TEST_METRIC
  done
  sleep 10
done


exit
