
#sed -i -e "s/101/0/g" /usr/sbin/policy-rc.d
yum install -y initscripts
yum install -y system-config-services
yum install -y python

bash -c "$(curl -sL $TARGET_SCRIPT)" -- --proxy --server $INSTANCE/api/ --token $API_TOKEN --telegraf --proxy_address localhost --proxy_port 4242 --overwrite_telegraf_config
while true; do /bin/echo 'Container $(hostname) is running.'; sleep 100; done;
