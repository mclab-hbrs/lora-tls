#!/bin/bash
echo "Host/Common Name = /etc/hosts"
HOST="HLK-Desktop"
cd certs

#prime256v1
cd prime256v1

openssl ecparam -genkey -name prime256v1 -out "ca-key.pem"
openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
openssl ecparam -genkey -name prime256v1 -out "server-key.pem"

openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
echo extendedKeyUsage = serverAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"

openssl ecparam -genkey -name prime256v1 -out "key.pem"
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
rm "extfile.cnf"
echo extendedKeyUsage = clientAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf

cd ..

#secp384r1
cd secp384r1

openssl ecparam -genkey -name secp384r1 -out "ca-key.pem"
openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
openssl ecparam -genkey -name secp384r1 -out "server-key.pem"

openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
echo extendedKeyUsage = serverAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"

openssl ecparam -genkey -name secp384r1 -out "key.pem"
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
rm "extfile.cnf"
echo extendedKeyUsage = clientAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf

cd ..

#brainpoolP256r1
cd brainpoolP256r1

openssl ecparam -genkey -name brainpoolP256r1 -out "ca-key.pem"
openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
openssl ecparam -genkey -name brainpoolP256r1 -out "server-key.pem"

openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
echo extendedKeyUsage = serverAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"

openssl ecparam -genkey -name brainpoolP256r1 -out "key.pem"
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
rm "extfile.cnf"
echo extendedKeyUsage = clientAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf

cd ..

#brainpoolP384r1
cd brainpoolP384r1

openssl ecparam -genkey -name brainpoolP384r1 -out "ca-key.pem"
openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
openssl ecparam -genkey -name brainpoolP384r1 -out "server-key.pem"

openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
echo extendedKeyUsage = serverAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"

openssl ecparam -genkey -name brainpoolP384r1 -out "key.pem"
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
rm "extfile.cnf"
echo extendedKeyUsage = clientAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf

cd ..

#brainpoolP512r1
cd brainpoolP512r1

openssl ecparam -genkey -name brainpoolP512r1 -out "ca-key.pem"
openssl req -new -x509 -days 365 -key "ca-key.pem" -sha384 -out "ca.pem"
openssl ecparam -genkey -name brainpoolP512r1 -out "server-key.pem"

openssl req -subj "/CN=$HOST" -sha384 -new -key "server-key.pem" -out "server.csr"
echo subjectAltName = DNS:$HOST,IP:192.168.29.56,IP:127.0.0.1 >> "extfile.cnf"
echo extendedKeyUsage = serverAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in "server.csr" -CA "ca.pem" -CAkey "ca-key.pem" -CAcreateserial -out "server-cert.pem" -extfile "extfile.cnf"

openssl ecparam -genkey -name brainpoolP512r1 -out "key.pem"
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
rm "extfile.cnf"
echo extendedKeyUsage = clientAuth >> "extfile.cnf"
openssl x509 -req -days 365 -sha384 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf

cd ..
