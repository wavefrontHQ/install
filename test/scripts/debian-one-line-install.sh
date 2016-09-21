
#sed -i -e "s/101/0/g" /usr/sbin/policy-rc.d
apt-get update -y
apt-get install curl -y
apt-get install python 2.7 -y
echo exit 0 > /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d

sudo bash -c "$(curl -sL $TARGET_SCRIPT)" -- --proxy --server $INSTANCE/api/ --token $API_TOKEN --telegraf --proxy_address localhost --proxy_port 4242 --overwrite_telegraf_config
while true; do /bin/echo 'Container $(hostname) is running.'; sleep 100; done;
