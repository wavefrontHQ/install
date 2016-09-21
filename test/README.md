# One-line Install Tests

This is a command line tool that will run a series of one-line install tests on different flavors of Linux.

1. It spins up containers based on each image we test on (currently ubuntu 14.04 and centos6 and centos7)
2. Runs a script on each container instance that installs dependencies
3. Runs one-line-install on each container with all options set (proxy AND telegraf)
4. Polls wavefront every 30 seconds.
5. The output will print either SUCCESS or FAILURE - when all containers have reported SUCCESS - all tests have passed.

If a container does not report SUCCESS after several minutes, check the logs directory. If you need to dig deeper, you can attach a shell to any running container using `docker exec -it <container name> /bin/bash` to dig deeper.

### Usage

```
./start-oli-tests.sh <target script> <wavefront instance> <API token> <metric to search for>`

Example:

./start-oli-tests.sh https://raw.githubusercontent.com/wavefrontHQ/install/telegraf/install.sh https://try.wavefront.com e26080f7-a26b-464b-8a0e-f1f765da6ce0 cpu_usage_idle
