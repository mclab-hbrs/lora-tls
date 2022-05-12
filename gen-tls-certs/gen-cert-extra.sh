#!/bin/bash
echo "Host/Common Name = /etc/hosts"
HOST="HLK-Desktop"

cd certs
# cd rsa2048
#
# ###RSA
# openssl genrsa -out "ca-key.pem" 2048
# openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
# openssl genrsa -out "server-key.pem" 2048
#
# openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
# echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
# echo extendedKeyUsage = serverAuth >> "extfile.cnf"
# openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"
#
# ###Create ClientAuth
# openssl genrsa -out key.pem 2048
# openssl req -subj '/CN=client' -new -key key.pem -out client.csr
# rm "extfile.cnf"
# echo extendedKeyUsage = clientAuth >> "extfile.cnf"
# openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf
#
# cd ..
cd ed25519

###ed25519
openssl genpkey -algorithm ed25519 -out "ca-key.pem"
openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
openssl genpkey -algorithm ed25519 -out "server-key.pem"

openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
echo extendedKeyUsage = serverAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"

openssl genpkey -algorithm ed25519 -out "key.pem"
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
rm "extfile.cnf"
echo extendedKeyUsage = clientAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf
