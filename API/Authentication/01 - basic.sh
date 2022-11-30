#!/bin/bash

NSX=10.221.109.5
USERNAME=admin
PASSWORD=VMware1!VMware1!

curl https://$NSX/policy/api/v1/infra/segments -X GET -k -u $USERNAME:$PASSWORD