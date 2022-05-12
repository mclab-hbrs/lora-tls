#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging as log
import warnings
import ntpath
import dill
import os
from lib.pcap_read_and_dissect import *
from lib.estimate_lora_airtime import *
from lib.results_and_plots import *

def get_worst_and_best_ciphers_by_size(df):
    mindf = df.loc[df.groupby('TLS_Version')['Overall_sizes'].idxmin()]   
    best_size_ciphers = mindf.index.values.tolist() 
    maxdf = df.loc[df.groupby('TLS_Version')['Overall_sizes'].idxmax()]
    worst_size_ciphers = maxdf.index.values.tolist() 

    return worst_size_ciphers, best_size_ciphers

def extract_dataframe_from_filename(pcap_filename, NiceName):
    # Raw DataFrame
    df = pd.DataFrame() # Init an empty data frame
    log.info(f'Dissect pcap File : {NiceName}')
    df = dissect_to_dataframe(pcap_filename) # dissect the pcap to a dataframe
    df = add_flowid_to_dataframe(df) # add flow id to it. Flow is a layer 1 flow. can be mutiple L2-Pakets
    df = add_direction_flag_to_dataframe(df) # Assumption. The first paket is sent by the sensors, therefore an uplink TODO
    return df

def extract_layer_sums(df):
    dict_layer_sums = defaultdict(lambda : 0) # Add a new dict. Will be a value to the previous dict.

    # Up and Down
    for Layer in df.Layer.unique(): # Go over all Layers in the dataframe
        layerSUM = df.loc[df['Layer'] == Layer, 'Size'].sum() # calc a sum
        dict_layer_sums[Layer+'_UpAndDown'] = layerSUM  # add it to the new subdic with the Layer as key and the sum as a value
        log.debug(f'Up and Down: {Layer} has a sum of {layerSUM}')
    
    # Down
    for Layer in df.Layer.unique():
        layerSUM = df.loc[(df['Layer'] == Layer) & (df['FlowDirection'] == 'DOWN'), 'Size'].sum()
        dict_layer_sums[Layer+'_Down'] = layerSUM 
        log.debug(f'Down: {Layer} has a sum of {layerSUM}')

    # Up
    for Layer in df.Layer.unique():
        layerSUM = df.loc[(df['Layer'] == Layer) & (df['FlowDirection'] == 'UP'), 'Size'].sum()
        dict_layer_sums[Layer+'_Up'] = layerSUM 
        log.debug(f'UP: {Layer} has a sum of {layerSUM}')
    
    return dict_layer_sums

def extract_number_of_layer_3_packets(df):
    number_of_pakets = df['ID'].max()
    return number_of_pakets

def extract_number_of_LoRa_packets(df):
    return len(df.index)

def extract_lora_airtime(df, LORAWAN_HEADER_SIZE, spreading_factor):
    dict_AirTime = defaultdict(lambda : 0)
    df['AirTime'] = np.nan

    for i, row in df.iterrows():
        AirTimeOfFragment = get_toa(n_size=int(LORAWAN_HEADER_SIZE+row['Size']),n_sf=spreading_factor)
        df.at[i,'AirTime'] = AirTimeOfFragment['t_packet']

    AirTimeSum = df['AirTime'].sum()
    AirTimeUP = df.loc[df['FlowDirection'] == 'UP', 'AirTime'].sum()
    AirTimeDOWN = df.loc[df['FlowDirection'] == 'DOWN', 'AirTime'].sum()
    dict_AirTime['AirTimeSum'] = AirTimeSum
    dict_AirTime['AirTimeUP'] = AirTimeUP
    dict_AirTime['AirTimeDOWN'] = AirTimeDOWN

    return dict_AirTime

def calc_duty_cycles(dict_pcap_reading):
    dict_DutyCycles = defaultdict(lambda : 0)

    # https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/
    # https://www.youtube.com/watch?v=G3GKT2HQQF8
    # https://jwcn-eurasipjournals.springeropen.com/track/pdf/10.1186/s13638-019-1502-5.pdf   

    # Time between packet SUBSEQUENT STARTS in the same subband
    # The calculation is a little bit tricky (percent stuff).
    # If we are allowed to send 1% of the time (T_on), we interested in 100% (T_on + T_off). This defines the minimum time between to Subsequent Start

    dict_DutyCycles['DutyCycle_Sum'] = {0.1 : dict_pcap_reading['AirTime']['AirTimeSum']/1000*(100/0.1), 1 : dict_pcap_reading['AirTime']['AirTimeSum']/1000*(100/1), 10 : dict_pcap_reading['AirTime']['AirTimeSum']/1000*(100/10)}
    dict_DutyCycles['DutyCycle_UP'] = {0.1 : dict_pcap_reading['AirTime']['AirTimeUP']/1000*(100/0.1), 1 : dict_pcap_reading['AirTime']['AirTimeUP']/1000*(100/1), 10 : dict_pcap_reading['AirTime']['AirTimeUP']/1000*(100/10)}
    dict_DutyCycles['DutyCycle_DOWN'] = {0.1 : dict_pcap_reading['AirTime']['AirTimeDOWN']/1000*(100/0.1), 1 : dict_pcap_reading['AirTime']['AirTimeDOWN']/1000*(100/1), 10 : dict_pcap_reading['AirTime']['AirTimeDOWN']/1000*(100/10)}

    # This is defined per Day, which is wrong. We need to define that per hour? Or does this matter?

    dict_DutyCycles['MaxTransmission2Day_Sum'] = {0.1 : 2*86400/dict_DutyCycles['DutyCycle_Sum'][0.1], 1 : 2*86400/dict_DutyCycles['DutyCycle_Sum'][1], 10 : 2*86400/dict_DutyCycles['DutyCycle_Sum'][10]}
    dict_DutyCycles['MaxTransmission2Day_UP'] = {0.1 : 2*86400/dict_DutyCycles['DutyCycle_UP'][0.1], 1 : 2*86400/dict_DutyCycles['DutyCycle_UP'][1], 10 : 2*86400/dict_DutyCycles['DutyCycle_UP'][10]}
    dict_DutyCycles['MaxTransmission2Day_DOWN'] = {0.1 : 2*86400/dict_DutyCycles['DutyCycle_DOWN'][0.1], 1 : 2*86400/dict_DutyCycles['DutyCycle_DOWN'][1], 10 : 2*86400/dict_DutyCycles['DutyCycle_DOWN'][10]}

    dict_DutyCycles['MaxTransmissionHour_Sum'] = {0.1 : 3600/dict_DutyCycles['DutyCycle_Sum'][0.1], 1 : 3600/dict_DutyCycles['DutyCycle_Sum'][1], 10 : 3600/dict_DutyCycles['DutyCycle_Sum'][10]}
    dict_DutyCycles['MaxTransmissionHour_UP'] = {0.1 : 3600/dict_DutyCycles['DutyCycle_UP'][0.1], 1 : 3600/dict_DutyCycles['DutyCycle_UP'][1], 10 : 3600/dict_DutyCycles['DutyCycle_UP'][10]}
    dict_DutyCycles['MaxTransmissionHour_DOWN'] = {0.1 : 3600/dict_DutyCycles['DutyCycle_DOWN'][0.1], 1 : 3600/dict_DutyCycles['DutyCycle_DOWN'][1], 10 : 3600/dict_DutyCycles['DutyCycle_DOWN'][10]}

    return dict_DutyCycles

def calc_results_dict(spreading_factor):

    fragmentation_size=250
    LORAWAN_HEADER_SIZE = 13
    # Storage for the raw dataframes and some results is in a nested dict called pcap_dataframes. Sorry.
    # Key of the highest level dict is the pcap filename i.e. "ECDHE-ECDSA-AES256-GCM-SHA384-brainpoolP512r1"
    # I.e. pcap_dataframes['TLS13_CHACHA20_POLY1305_SHA256-ed25519']
    # Inside are another dicts and a pandas data frame which holds the results. These are:
    # - DutyCycle : DICT
    # - LayerSum : DICT
    # - PacketCounts : DICT
    # - DataFrameRaw : DataFrameRaw
    pcap_dicts = {}

    # get all the filenames in the pcap folder.
    filenames = glob("./pcaps/*.PCAP")

    # Go over all filenames. 
    for pcap_filename in filenames:
        dict_pcap_reading = defaultdict(lambda : 0) # Init a dict for each new pcap

        NiceName = ntpath.basename(pcap_filename).split('.')[0] # Nice Name. TODO Split into Cipher Suites Functions
        log.info(f'Evaluating pcap File : {NiceName}')
        dict_pcap_reading['DataFrameRaw'] = extract_dataframe_from_filename(pcap_filename, NiceName) # Save the DataFrame to the Dict with value DataFrameRaw
        curDF = dict_pcap_reading['DataFrameRaw'] # lazy name for all future things

        log.info("Evaluating pcap done, saved rawdataframe")
        
        # Layer Sums which shows how many byte are used for each communication layer (IP, TCP, TLS)
        dict_pcap_reading['LayerSum'] = extract_layer_sums(curDF) # add the layer sum dict, to the pcap dict

        # Number of Pakets and Fragements, Lora Fragments splitted based on the fragmentation size
        dict_pcap_reading['LoRaDataFrameRaw'] = split_dataframe_into_lora_fragments(fragmentation_size, curDF) # Save the DataFrame to the Dict with value DataFrameRaw
        curDF_LoRa = dict_pcap_reading['LoRaDataFrameRaw'] # lazy name for all future things

        # Add a new dict. We will use that dict twice, therefore the init is here.
        dict_counts = defaultdict(lambda : 0) 
        dict_counts['L3Pakets'] = extract_number_of_layer_3_packets(curDF)
        dict_counts['LoRaFragments'] = extract_number_of_LoRa_packets(curDF_LoRa) 
        dict_pcap_reading['PacketCounts'] = dict_counts

        # Add AirTime to LoRa Fragments using LoRa calculations
        dict_pcap_reading['AirTime'] = extract_lora_airtime(curDF_LoRa, LORAWAN_HEADER_SIZE, spreading_factor)

        # Add Duty Cycle Calculations
        dict_pcap_reading['DutyCycle'] = calc_duty_cycles(dict_pcap_reading)

        #finally, add the pcap dict.
        pcap_dicts[NiceName] = dict_pcap_reading
    return pcap_dicts

def parse_tls_ciphher(label):
    ciphers = ['AES_128_GCM_SHA256','AES_256_GCM_SHA384','AES_128_CCM_SHA256','CHACHA20_POLY1305_SHA256','DHE_RSA_WITH_AES_256_GCM_SHA384', 'ECDHE-ECDSA-AES128-SHA256', 'ECDHE-ECDSA-AES256-GCM-SHA384', 'ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES256-SHA384']
    curves = ['brainpoolP512r1', 'prime256v1', 'brainpoolP384r1', 'secp384r1', 'brainpoolP256r1','ED25519','RSA2048']
    
    cipher = 'None'
    for cipher_check in ciphers:
        if cipher_check.upper() in label:
            cipher = cipher_check.upper()
            
    curve = 'None'
    for curve_check in curves:
        if curve_check.upper() in label:
            curve = curve_check.upper()
            
    return cipher, curve


def cluster_TLS_ciphers_and_layer(pcap_dicts, direction):
    labels = list(pcap_dicts.keys())
    TLS_Version = [] 
    TLS_Cipher = [] 
    TLS_Curve = [] 
    L3_Packets = [] 
    IP_sizes = []
    L4_sizes = []
    IP_and_L4_sizes = []
    TLS_sizes = []
    LoRa_Fragments = []

  
    for label in labels:
        TLS_Version.append(label.split('_')[0])
        cipher, curve = parse_tls_ciphher(label)
        TLS_Cipher.append(cipher)
        TLS_Curve.append(curve)


        if direction == "UpAndDown":
            LoRa_Fragments.append(pcap_dicts[label]['PacketCounts']['LoRaFragments'])
            L3_Packets.append(pcap_dicts[label]['PacketCounts']['L3Pakets'])
            IP_sizes.append(pcap_dicts[label]['LayerSum']['IP_UpAndDown'])
            TLS_sizes.append(pcap_dicts[label]['LayerSum']['TLS_UpAndDown'])
            if "TCP_UpAndDown" in pcap_dicts[label]['LayerSum']:
                TCPSize = pcap_dicts[label]['LayerSum']['TCP_UpAndDown']
                L4_sizes.append(TCPSize)
            elif "UDP_UpAndDown" in pcap_dicts[label]['LayerSum']:
                UDPSize = pcap_dicts[label]['LayerSum']['UDP_UpAndDown']
                L4_sizes.append(UDPSize)
            else:
                log.info('OHOHO')
                break
        if direction == "Down":
            LoRa_Fragments.append(np.nan) #TODO
            L3_Packets.append(np.nan) #TODO
            IP_sizes.append(pcap_dicts[label]['LayerSum']['IP_Down'])
            TLS_sizes.append(pcap_dicts[label]['LayerSum']['TLS_Down'])
            if "TCP_Down" in pcap_dicts[label]['LayerSum']:
                TCPSize = pcap_dicts[label]['LayerSum']['TCP_Down']
                L4_sizes.append(TCPSize)
            elif "UDP_Down" in pcap_dicts[label]['LayerSum']:
                UDPSize = pcap_dicts[label]['LayerSum']['UDP_Down']
                L4_sizes.append(UDPSize)
            else:
                log.info('OHOHO')
                break
        if direction == "Up":
            LoRa_Fragments.append(np.nan) #TODO
            L3_Packets.append(np.nan) #TODO
            IP_sizes.append(pcap_dicts[label]['LayerSum']['IP_Up'])
            TLS_sizes.append(pcap_dicts[label]['LayerSum']['TLS_Up'])
            if "TCP_Up" in pcap_dicts[label]['LayerSum']:
                TCPSize = pcap_dicts[label]['LayerSum']['TCP_Up']
                L4_sizes.append(TCPSize)
            elif "UDP_Up" in pcap_dicts[label]['LayerSum']:
                UDPSize = pcap_dicts[label]['LayerSum']['UDP_Up']
                L4_sizes.append(UDPSize)
            else:
                log.info('OHOHO')
                break

    IP_and_L4_sizes = np.add(IP_sizes, L4_sizes)
    Overall_sizes = np.add(IP_and_L4_sizes, TLS_sizes)

    df = pd.DataFrame(list(zip(TLS_Version, TLS_Cipher, TLS_Curve, IP_sizes, L4_sizes, TLS_sizes, IP_and_L4_sizes,Overall_sizes,L3_Packets,LoRa_Fragments)), 
            columns =['TLS_Version','TLS_Cipher','TLS_Curve','IP_sizes','L4_sizes','TLS_sizes', 'IP_and_L4_sizes','Overall_sizes','L3_Packets','LoRa_Fragments'], index=labels)

    return df

    
def cluster_due_to_links(pcap_dict_exp):
    df_cluster_upanddown = pd.DataFrame() # Init an empty data frame
    df_cluster_upanddown = cluster_TLS_ciphers_and_layer(pcap_dict_exp, 'UpAndDown')
    df_cluster_down = pd.DataFrame() # Init an empty data frame
    df_cluster_down = cluster_TLS_ciphers_and_layer(pcap_dict_exp, 'Down')
    df_cluster_up = pd.DataFrame() # Init an empty data frame
    df_cluster_up = cluster_TLS_ciphers_and_layer(pcap_dict_exp, 'Up')
    return df_cluster_upanddown, df_cluster_down, df_cluster_up


def main():
    # Lets Go.
    FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
    log.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),format=FORMAT)
    log.getLogger('numexpr').setLevel(logging.WARNING)
    log.getLogger('matplotlib').setLevel(logging.WARNING)

    # The recalc flag. If set to true, the pcaps are read again and saved as a dill/pickle file.
    recalc = False

    spreading_factor_list = [7, 8 ,9 ,10 ,11 ,12]
    results_dict = {}
    # Reference Names for the paper. This is hard coded. 
    cipher_size_paper_reference = {'DTLS': {'DTLS12_ECDHE-ECDSA-AES256-SHA384-SECP384R1': 'L', 'DTLS12_ECDHE-ECDSA-AES128-GCM-SHA256-PRIME256V1': 'S'},
                                   'TLS12': {'TLS12_DHE_RSA_WITH_AES_256_GCM_SHA384-RSA2048': 'L', 'TLS12_ECDHE-ECDSA-AES128-SHA256-PRIME256V1': 'S'},
                                   'TLS13': {'TLS13_AES_256_GCM_SHA384_BRAINPOOLP512R1': 'L', 'TLS13_AES_128_GCM_SHA256_ED25519': 'S'}}

    log.info(f'Lets Go.')
    log.info(f'All Python warning i.e. matplotlib are ignored due to readability of the log')
    warnings.filterwarnings("ignore")

    if recalc:
        log.info(f'Recalc Flag is set to true, recalcing and dissecting pcaps files')
        for SF in spreading_factor_list:
            log.info(f' Spreading factor is : {SF}')
            results_dict[SF] = calc_results_dict(SF)
        with open('./pcaps/parsed-pcaps.pkl', 'wb') as f:
            dill.dump(results_dict, f)
    else:
        with open('./pcaps/parsed-pcaps.pkl', 'rb') as f:
            log.info(f'Reading pcap files from dill storage')
            results_dict = dill.load(f)

    # All about sizes will be calculated with SF7, does not matter hower since it is all the same.
    pcap_dict_exp = results_dict[7]
    log.info(f'Clustering the results in UpDown/Down/Up')
    df_cluster_upanddown, df_cluster_down, df_cluster_up = cluster_due_to_links(pcap_dict_exp)


    # Bar Chart of protocol sizes, TLS, IP etc.
    log.info(f'Getting larges and smallets ciphers for the combined up and downlink')
    worst_size_ciphers, best_size_ciphers = get_worst_and_best_ciphers_by_size(df_cluster_upanddown)
    log.info(f'Largest Ciphers {worst_size_ciphers}')
    log.info(f'Smallest Ciphers {best_size_ciphers}')
    log.info(f'Plotting bar chart of protocols (FIG.3)')
    plot_bar_chart_of_protocols(df_cluster_upanddown,worst_size_ciphers,best_size_ciphers,cipher_size_paper_reference)


    ## Plot the three size comparisons. 
    log.info(f'Plotting box plots of different sizes for the TLS ciphers (FIG. 2)')
    plot_boxpolot_of_tls_ciphers(df_cluster_upanddown,'boxplot-cipher-suite-vs-size.pdf')
    plot_boxpolot_of_tls_ciphers(df_cluster_down,'boxplot-cipher-suite-vs-size-down.pdf')
    plot_boxpolot_of_tls_ciphers(df_cluster_up,'boxplot-cipher-suite-vs-size-up.pdf')

    # Have a look at the uplink
    log.info(f'Plotting box plot for the uplink comparison')
    plot_uplink_airtime_spreading_factor(results_dict, spreading_factor_list)

    log.info(f'Plotting bar chart of protocols for the maximum number of handshakes in two days downlink (FIG. 5)')
    plot_two_days_maximum_handshakes(results_dict, spreading_factor_list, worst_size_ciphers, best_size_ciphers,cipher_size_paper_reference)

    log.info(f'Plotting line chart of max number of sensors per GW (FIG. 6)')
    plot_line_chart_number_of_sensors_per_gw(results_dict, spreading_factor_list, worst_size_ciphers, best_size_ciphers)

    return 0
    
if __name__== "__main__":
  main()
