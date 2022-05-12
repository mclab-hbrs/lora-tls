#!/usr/bin/env python3
import threading
import time
import subprocess
import os
import signal

ciphers = ["TLS_CHACHA20_POLY1305_SHA256"]
curves = ["prime256v1","secp384r1","brainpoolP256r1","brainpoolP384r1","brainpoolP512r1"]

#secp256r1 = prime256v1

currcipher = ""
currcurve = ""
certdir = ""

start = 0
stop = 0

def server():
    global currcurve, currcipher, start, stop, certdir
    while stop != 1:
        if start:
            curvecmd = " -curves " + currcurve
            ciphercmd = " -ciphersuites " + currcipher
            cmd = 'openssl s_server -cert ' + certdir + 'server-cert.pem -tls1_3 -key ' + certdir + 'server-key.pem -accept 8080 -Verify 1 -CAfile ' + certdir + 'ca.pem -no_resumption_on_reneg -num_tickets 0 -brief' + curvecmd + ciphercmd
            print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            time.sleep(5)
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)

def client():
    global currcurve, currcipher, start, stop, certdir
    while stop != 1:
        if start:
            curvecmd = " -curves " + currcurve
            ciphercmd = " -ciphersuites " + currcipher
            cmd = 'echo "0000000000" | openssl s_client -tls1_3 -connect 127.0.0.1:8080 -cert ' + certdir + 'cert.pem -key ' + certdir + 'key.pem -CAfile ' + certdir + 'ca.pem -brief' + curvecmd + ciphercmd
            print(cmd)
            time.sleep(2)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            time.sleep(3)
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)

def tshark():
    global currcurve, currcipher
    while stop != 1:
        if start:
            cmd = 'touch pcap-tls13/TLS13_' + currcipher[4:] + "_" + currcurve.upper() + ".pcap"
            subprocess.Popen(cmd, shell=True)
            cmd = 'chmod 777 pcap-tls13/TLS13_' + currcipher[4:] + "_" + currcurve.upper() + ".pcap"
            subprocess.Popen(cmd, shell=True)
            cmd = 'sudo tshark -i lo -a duration:4 -F pcap -w pcap-tls13/TLS13_' + currcipher[4:] + "_" + currcurve.upper() + ".pcap"
            subprocess.Popen(cmd, shell=True)
            time.sleep(1)

tshark = threading.Thread(target=tshark)
server = threading.Thread(target=server)
client = threading.Thread(target=client)

server.start()
client.start()
tshark.start()


for cipher in ciphers:
    print(cipher)
    for curve in curves:
        currcurve = curve
        currcipher = cipher
        certdir = "certs/" + curve + "/"
        start = 1
        time.sleep(1)
        start = 0
        time.sleep(8)
        print("finish")

stop = 1
server.join()
client.join()
tshark.join()
exit()
