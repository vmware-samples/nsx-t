#!/bin/bash

NSX=10.221.109.5
USERNAME=admin
PASSWORD=VMware1!VMware1!


# Create certificate
openssl req -newkey rsa:2048  -nodes -keyout piuser.key -x509 -days 365 -out piuser.crt -subj "/C=US/ST=California/L=Palo Alto/O=VMware/CN=certauth-test" -sha256

# Convert to p12 format (for CURL)
echo '\n' > emptypw.txt
openssl pkcs12 -export -out piuser.pfx -inkey piuser.key -in piuser.crt -passout file:emptypw.txt
openssl pkcs12 -in piuser.pfx -out piuser.p12 -nodes -passin file:emptypw.txt
rm -rf emptypw.txt

# Remove First and last line + \n
CERTIFICATE=$(sed '1d; $d' piuser.crt |  while read line; do echo -n "$line "; done)

# Create Principle Identity
curl https://$NSX/api/v1/trust-management/principal-identities/with-certificate -k -u "$USERNAME:$PASSWORD" -X POST -H "content-type:application/json" -d "{\"name\": \"piuser\", \"node_id\": \"api\", \"role\": \"enterprise_admin\", \"is_protected\": \"true\",\"certificate_pem\": \"-----BEGIN CERTIFICATE-----\n$CERTIFICATE\n-----END CERTIFICATE-----\n\"}"

# Create something
curl https://$NSX/policy/api/v1/infra/tier-0s/MyT0 --cert piuser.p12 -k -X PATCH -H "content-type:application/json" -d "{\"resource_type\": \"Tier0\",\"id\": \"MyT0\"}"

# Delete PI
curl https://$NSX/policy/api/v1/infra/tier-0s/MyT0 --cert piuser.p12 -k -X DELETE
curl https://$NSX/api/v1/trust-management/principal-identities/with-certificate/e25320ee-5c7b-4896-b0ce-02a11edaae5d -k -u "$USERNAME:$PASSWORD" -X DELETE
