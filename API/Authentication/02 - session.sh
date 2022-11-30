#!/bin/bash

NSX=10.221.109.5
USERNAME=admin
PASSWORD=VMware1!VMware1!


# Get the cookie and token
curl https://$NSX/api/session/create -k -c cookies.txt -D headers.txt -X POST -d "j_username=$USERNAME&j_password=$PASSWORD"

# Use the cookie and the token
curl -k -b cookies.txt -H "`grep X-XSRF-TOKEN headers.txt`" https://$NSX/policy/api/v1/infra/segments
