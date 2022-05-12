#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scapy.all import *
import pandas as pd
load_layer("tls")
import logging as log
import numpy as np
from lib.estimate_lora_airtime import *

def dissect(pcap_file):
    packets = rdpcap(pcap_file)
    pkg_sizes = {}
    pkg_addresses = {}
    for i, packet in enumerate(packets):
        header_sizes = defaultdict(lambda : 0)
        ip_addresses = defaultdict(lambda : 0)

        num_layers = len(packet.layers())
        tls_header_found = False

        for layer_num in range(num_layers):
            layer = packet.getlayer(layer_num)
            layer_id = layer.layers()[0]
            layer_name = layer.name

            # Change Raw Layer to TLS
            if layer_id is Raw:
                layer_name = "TLS"

            header_sizes[layer_name] += len(layer) - len(layer.payload)

        pkg_sizes[i] = header_sizes

        if packet.haslayer(IP):
            ip=packet.getlayer(IP)
            sadd = ip.src
            dadd = ip.dst
        else:
            log.INFO(f'Did not find IP in ID {pktID}. Danger')
        if TCP in packet:
          sport=packet[TCP].sport
          dport=packet[TCP].dport
        elif UDP in packet:
          sport=packet[UDP].sport
          dport=packet[UDP].dport
        else:
          log.INFO(f'Did not find a TCP or UDP Port in ID {pktID}. Danger')

        ip_addresses['src'] = str(sadd)+":"+str(sport)
        ip_addresses['dst'] = str(dadd)+":"+str(dport)
        pkg_addresses[i] = ip_addresses
        
    return packets, pkg_sizes, pkg_addresses


def add_flowid_to_dataframe(df):
    # Add a flow ID. 
    df["Layer1FlowID"] = np.nan
   
    # I love SO: https://stackoverflow.com/questions/48673046/get-index-where-value-changes-in-pandas-dataframe-column
    indexChangeDictFlow = {k: s.index[s].tolist() for k, s in df.ne(df.shift()).items()} # TODO the last index is missing
    flowIDcounter = 0
    for i in range(len(indexChangeDictFlow['ipSRC'])-1): 
        #print(i, indexChangeDictFlow['ipSRC'][i])

        for j in range(indexChangeDictFlow['ipSRC'][i], indexChangeDictFlow['ipSRC'][i+1]):
            df.at[j, 'Layer1FlowID'] = flowIDcounter
        flowIDcounter += 1

    for j in range(indexChangeDictFlow['ipSRC'][-1], df.index[-1]+1):
        df.at[j, 'Layer1FlowID'] = flowIDcounter

    return df

def add_direction_flag_to_dataframe(df):
    # Add a Direction Flag
    df["FlowDirection"] = 'NONE'
    sensorIPandPort = df['ipSRC'].iloc[0]
    gwIPandPort = df['ipDST'].iloc[0]

    df.loc[(df.ipSRC == sensorIPandPort),'FlowDirection']='UP'
    df.loc[(df.ipSRC == gwIPandPort),'FlowDirection']='DOWN'
    # Assumption. The first paket is sent by the sensors, therefore an uplink
    return df

def dissect_to_dataframe(pcap_file):
    pkgs, header_sizes, ip_addresses = dissect(pcap_file)

    df  = pd.DataFrame({'ID': pd.Series([], dtype='str'),
                        'Layer': pd.Series([], dtype='str'),
                        'Size': pd.Series([], dtype='int'),
                        'ipSRC': pd.Series([], dtype='str'),
                        'ipDST': pd.Series([], dtype='str')})
    for pktID, d_protos in header_sizes.items():
        log.debug(f'Looking at the Paket with the ID {pktID}')
        for proto in d_protos:
            log.debug(f'In Frame with the ID {pktID}, Looking at the Protocol {proto}')
            pktSize = d_protos[proto]
            log.debug(f'The protocol size is {pktSize}')
            df.loc[len(df)] = [int(pktID),proto,int(pktSize),str(ip_addresses[pktID]['src']),str(ip_addresses[pktID]['dst'])]
    return df

def split_dataframe_into_lora_fragments(fragmentation_size, df):
    df_fragments = df.groupby(['Layer1FlowID','FlowDirection']).sum()
    df_lora_fragments  = pd.DataFrame({'ID': pd.Series([], dtype='str'),
                        'Layer1FlowID': pd.Series([], dtype='int'),
                        'FlowDirection': pd.Series([], dtype='str'),
                        'Size': pd.Series([], dtype='int')})

    ID = 0
    for index, row in df_fragments.iterrows():
        if row['Size'] > fragmentation_size:
            log.debug("This row gets fragmented")
            num_of_full_fragments = int(row['Size'] / fragmentation_size)
            for i in range(num_of_full_fragments):
                df_lora_fragments.loc[len(df_lora_fragments)] = [ID,index[0],index[1],fragmentation_size]
                ID +=1
            # Add the rest
            df_lora_fragments.loc[len(df_lora_fragments)] = [ID,index[0],index[1],row['Size'] % fragmentation_size]

        else:
            df_lora_fragments.loc[len(df_lora_fragments)] = [ID,index[0],index[1],row['Size']]
            ID +=1

    return df_lora_fragments