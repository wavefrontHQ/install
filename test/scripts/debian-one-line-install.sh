
#sed -i -e "s/101/0/g" /usr/sbin/policy-rc.d
apt-get update -y
apt-get install curl -y
echo exit 0 > /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d

bash -c "$(curl -sL $TARGET_SCRIPT)" -- --proxy --server $INSTANCE/api/ --token $API_TOKEN --telegraf --proxy_address localhost --proxy_port 4242

while :
do
	echo "Container is Running."
	sleep 10
done
