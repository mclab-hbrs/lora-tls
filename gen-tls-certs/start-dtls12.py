#!/usr/bin/env python3
import threading
import time
import subprocess
import os
import signal

ciphers = ["ECDHE-ECDSA-AES128-SHA256", "ECDHE-ECDSA-AES256-SHA384", "ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-ECDSA-AES256-GCM-SHA384"]
curves = ["prime256v1","secp384r1"]

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
            ciphercmd = " -cipher " + currcipher
            cmd = 'openssl s_server -cert ' + certdir + 'server-cert.pem -dtls1_2 -no_ticket -key ' + certdir + 'server-key.pem -accept 8080 -Verify 1 -CAfile ' + certdir + 'ca.pem -no_resumption_on_reneg -num_tickets 0 -quiet' + curvecmd + ciphercmd
            print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            time.sleep(7)
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)

def client():
    global currcurve, currcipher, start, stop, certdir
    while stop != 1:
        if start:
            curvecmd = " -curves " + currcurve
            ciphercmd = " -cipher " + currcipher
            cmd = 'echo "0000000000" | openssl s_client -dtls1_2 -connect 127.0.0.1:8080 -cert ' + certdir + 'cert.pem -key ' + certdir + 'key.pem -CAfile ' + certdir + 'ca.pem -quiet' + curvecmd + ciphercmd
            print(cmd)
            time.sleep(2)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            time.sleep(5)
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)

def tshark():
    global currcurve, currcipher
    while stop != 1:
        if start:
            cmd = 'touch pcap-dtls12/DTLS12_' + currcipher.replace("-","_") + "_" + currcurve.upper() + ".pcap"
            subprocess.Popen(cmd, shell=True)
            cmd = 'chmod 777 pcap-tls12/DTLS12_' + currcipher.replace("-","_") + "_" + currcurve.upper() + ".pcap"
            subprocess.Popen(cmd, shell=True)
            cmd = 'sudo tshark -i lo -a duration:4 -F pcap -w pcap-dtls12/DTLS12_' + currcipher.replace("-","_") + "_" + currcurve.upper() + ".pcap"
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
        time.sleep(10)
        print("finish")

stop = 1
server.join()
client.join()
tshark.join()
exit()
