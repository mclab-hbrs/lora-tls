#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, paramiko, time, subprocess, os, signal
import zipfile

def set_SF_remote(SF):
    hostname = "10.20.111.52"
    port = "22"
    password = "******"
    username = "pi"
    command_front = "sudo python3 michael.py "
    command_payload = "00"

    if SF == 7:
        command_payload = "01"
    elif SF == 8:
        command_payload = "02"
    elif SF == 9:
        command_payload = "03"
    elif SF == 10:
        command_payload = "04"
    elif SF == 11:
        command_payload = "05"
    elif SF == 12:
        command_payload = "06"
    else:
        print("Danger! Unknown SF")
 
    command = command_front + command_payload
    print(command)

    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(hostname, port=port, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command)
        lines = stdout.readlines()
        print(lines)
    finally:
        client.close()

    return 0


def send_bytes_remote(byte_string):
    hostname = "10.20.111.52"
    port = "22"
    password = "mmk4hbrs"
    username = "pi"
    command_front = "sudo python3 michael-loop.py "
    command_payload = byte_string
    command = command_front + command_payload
    print(command)

    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(hostname, port=port, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command, timeout=30)
        lines = stdout.readlines()
        print(lines)
    finally:
        client.close()

    return 0

def start_local_measurement(num_of_char, cool_down_time, SpreadingFactor):
    character_to_send = "0"
    print(num_of_char*character_to_send)
    DataFilename = str(num_of_char)+"-Char"+"-"+str(SpreadingFactor)+"-SF"
    cmd = 'python gather.py ' + DataFilename
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    #time.sleep(0.1)
    set_SF_remote(SpreadingFactor)
    send_bytes_remote(str(num_of_char*character_to_send))
    time.sleep(1)
    p.terminate()
    try:
        outs = p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()

    time.sleep(cool_down_time)
    zip_file = zipfile.ZipFile(DataFilename+'.zip', 'w')
    zip_file.write(DataFilename+'.complexfloat32', compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    os.remove(DataFilename+'.complexfloat32')


def main(): 

    SpreadingFactor = 7
    cool_down_time = 1
    min_char = 20
    max_char = 480
    sleep_period = 1

    #set_SF_remote(SpreadingFactor)
    #send_bytes_remote('000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')

    #return 0

    for i in range(min_char,max_char,2):
        for SpreadingFactor in range(7,13):
            print(f"char is {i} and SF is {SpreadingFactor}")
            start_local_measurement(i, cool_down_time, SpreadingFactor)
        print("cooling of. Lets wait a little bit")
        time.sleep(5)

if __name__ == '__main__':
    main()
