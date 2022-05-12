# Version https://github.com/openssl/openssl/pull/11782 https://github.com/bernd-edlinger/openssl/tree/enable_brainpool_for_tls13_1
./config

make

sudo make install

# Certs
./gen-cert

# Server:
openssl s_server -cert certs/server-cert.pem -key certs/server-key.pem -accept 8080 -Verify 1 -num_tickets 0 -debug 

# Client:
echo "000000000" | openssl s_client -connect 127.0.0.1:8080 -cert certs/cert.pem -key certs/key.pem