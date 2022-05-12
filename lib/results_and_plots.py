#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
import seaborn as sns

params = {
    'text.usetex': True,
    'text.latex.preamble' : [r'\boldmath'],
    'figure.figsize': [4.5, 5.5],
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 12,
    'legend.handletextpad': 0.1,
    'legend.borderpad': 0.2,
    'legend.columnspacing': 0.5,
    'legend.labelspacing': 0.5,
    'figure.autolayout': True,
    'font.family' : 'serif',
    'font.serif': 'cmr10',
    'axes.spines.top' : False,
    'axes.spines.right' : False,
    'axes.grid': True,
    'grid.linewidth': 0.25,
    'grid.alpha': 0.25
}
plt.rcParams.update(params)
numberOfPlottingFeatures = 2
colors = sns.color_palette("Blues", numberOfPlottingFeatures)
linestyles = ['-', '--', '-.', ':']


def plot_uplink_airtime_spreading_factor(results_dict, spreading_factor_list):
    fig, ax = plt.subplots(figsize=(5,2.5))
    fig.subplots_adjust(bottom=0.4)

    cipher_list = results_dict[7].keys()
    plot_df = pd.DataFrame(index = cipher_list,columns=spreading_factor_list,dtype=float)

    for SF in results_dict.keys():
        curSFdict = results_dict[SF]
        for cipher in curSFdict.keys():
            plot_df.at[cipher,SF] = results_dict[SF][cipher]['AirTime']['AirTimeUP']/1000 # IN SECONDS HERE

    plot_df.boxplot(column=[7,8,9,10,11,12], ax=ax)
    plt.axhline(y=36, color='r', linestyle='--')
    style = dict(size=15, color='red')
    ax.text(1, 40, r"1\% duty cycle per hour", **style)
    ax.set_ylabel('Uplink Airtime [s]')
    ax.set_xlabel('Spreading factor')
    ax.set_ylim(1,120)
    plt.suptitle('') 
    ax.set_title("")

    plt.savefig('./figures/Uplink-Airtime-per-SF.pdf',format='pdf',bbox_inches='tight',dpi=700)


def plot_two_days_maximum_handshakes(results_dict, spreading_factor_list, worst_size_ciphers, best_size_ciphers,cipher_size_paper_reference):
    cipher_list = best_size_ciphers + worst_size_ciphers

    fig, ax = plt.subplots(figsize=(5,3.5))
    fig.subplots_adjust(bottom=0.4)

    plot_df = pd.DataFrame(columns=[],index = spreading_factor_list)

    for cipher in cipher_list:
        for SF in spreading_factor_list:
            cur_Transmission = results_dict[SF][cipher] 
            plot_df.at[SF,cipher] = cur_Transmission['DutyCycle']['MaxTransmission2Day_DOWN'][10]+cur_Transmission['DutyCycle']['MaxTransmission2Day_DOWN'][1]

    numberOfPlottingFeatures = len(cipher_list)
    colors = sns.color_palette("Blues", numberOfPlottingFeatures)

    cipher_list_sorted = plot_df.sum(axis=0).sort_values().keys().to_list()
    plot_df = plot_df[cipher_list_sorted]

    plot_df = plot_df.rename(columns={'DTLS12_ECDHE-ECDSA-AES256-SHA384-SECP384R1': 'DTLS1.2-L', 'DTLS12_ECDHE-ECDSA-AES128-GCM-SHA256-PRIME256V1': 'DTLS1.2-S',
    'TLS12_DHE_RSA_WITH_AES_256_GCM_SHA384-RSA2048': 'TLS1.2-L', 'TLS12_ECDHE-ECDSA-AES128-SHA256-PRIME256V1': 'TLS1.2-S',
    'TLS13_AES_256_GCM_SHA384_BRAINPOOLP512R1': 'TLS1.3-L', 'TLS13_AES_128_GCM_SHA256_ED25519': 'TLS1.3-S'})

    plot_df.plot.bar(rot=0,ax=ax, color=colors,width=0.8)
    ax.set_ylabel('Max. handshakes in 48h')
    ax.set_xlabel('Spreading Factor')



    plt.savefig('./figures/TLS-Handshakes-per-2Days-Ciphers.pdf',format='pdf',bbox_inches='tight',dpi=700)

def scatter_plot_size(df):
    fig, ax = plt.subplots(figsize=(10,10))
    fig.subplots_adjust(bottom=0.4)
    plt.scatter(df.TLS_Cipher, df.Overall_sizes, c=df.TLS_Curve)
    plt.savefig('./figures/cipher_scatter.pdf',format='pdf',bbox_inches='tight',dpi=700)


def plot_bar_chart_of_protocols(df,worst_size_ciphers,best_size_ciphers,cipher_size_paper_reference):

    numberOfPlottingFeatures = 3
    colors = sns.color_palette("Blues", numberOfPlottingFeatures)

    cipherlist = worst_size_ciphers + best_size_ciphers

    df = df.loc[cipherlist]
    df = df.sort_values(by=['TLS_Version'])

    fig, ax = plt.subplots(figsize=(5,3.65))
    fig.subplots_adjust(bottom=0.4)
    
    barWidth = 1

    ax.bar(df.index.values.tolist(), df["IP_sizes"].tolist(), label='IP', edgecolor='white',width=barWidth, color = colors[0])
    ax.bar(df.index.values.tolist(), df["L4_sizes"].tolist(), bottom=df["IP_sizes"].tolist(), label='TCP/UDP', edgecolor='white',width=barWidth,color = colors[1])
    ax.bar(df.index.values.tolist(), df["TLS_sizes"].tolist(), bottom=df["IP_and_L4_sizes"].tolist(), label='(D)TLS', edgecolor='white',width=barWidth,color = colors[2])

    curlabels_ciphers = ax.get_xticklabels()
    ax.set_xticklabels( ('DTLS1.2-L', 'DTLS1.2-S','TLS1.2-L','TLS1.2-S', 'TLS1.3-L','TLS1.3-S') )
    ax.yaxis.grid()
    ax.set_ylabel('Size [Byte]')
    ax.set_xlabel('')
    ax.legend()

    plt.xticks(rotation=45)
    plt.legend(frameon=False)
    plt.suptitle('') 
    ax.set_title('')

    plt.savefig('./figures/cipher-suite-vs-size.pdf',format='pdf',bbox_inches='tight',dpi=700)

    return


def plot_boxpolot_of_tls_ciphers(df,name):
    fig, ax = plt.subplots(figsize=(5,2.6))
    fig.subplots_adjust(bottom=0.4)

    df.boxplot(column=['Overall_sizes'], by='TLS_Version', ax=ax)
    ax.set_ylabel('Size [Byte]')
    ax.set_xlabel('TLS variant')
    ax.set_xticklabels( ('DTLS1.2', 'TLS1.2', 'TLS1.3') )
    ax.set_ylim(0,7000)
    plt.suptitle('') 
    ax.set_title("")

    ax.yaxis.set_major_locator(plt.MaxNLocator(4))

    plt.savefig('./figures/'+name,format='pdf',bbox_inches='tight',dpi=700)

    return 

def plot_line_chart_number_of_sensors_per_gw(results_dict, spreading_factor_list, worst_size_ciphers, best_size_ciphers):

    min_number_of_sensors = 100
    max_number_of_sensors = 50000
    step = 1000
    sensor_number_list = np.arange(min_number_of_sensors, max_number_of_sensors, step).tolist()

    cipher = best_size_ciphers[2]

    plot_df_10 = pd.DataFrame(columns=spreading_factor_list, index = sensor_number_list,dtype=int)
    plot_df_1 = pd.DataFrame(columns=spreading_factor_list, index = sensor_number_list,dtype=int)

    for SF in spreading_factor_list:
        cur_Transmission = results_dict[SF][cipher] 
        for i in sensor_number_list:
            plot_df_10.at[i, SF] = (cur_Transmission['DutyCycle']['DutyCycle_DOWN'][10]*((i-(i/10)))/3600/24) # Assumption every 10th sensor can be put in another band # in DAYS!!

    fig, ax = plt.subplots(figsize=(5,3.2))
    fig.subplots_adjust(bottom=0.4)

    numberOfPlottingFeatures = 6
    colors = sns.color_palette("Blues", numberOfPlottingFeatures)

    ax.plot(plot_df_10.index.values.tolist(),plot_df_10[7].tolist(),label="SF 7",color=colors[0])
    ax.plot(plot_df_10.index.values.tolist(),plot_df_10[8].tolist(),label="SF 8",color=colors[1])
    ax.plot(plot_df_10.index.values.tolist(),plot_df_10[9].tolist(),label="SF 9",color=colors[2])
    ax.plot(plot_df_10.index.values.tolist(),plot_df_10[10].tolist(),label="SF 10",color=colors[3])
    ax.plot(plot_df_10.index.values.tolist(),plot_df_10[11].tolist(),label="SF 11",color=colors[4])
    ax.plot(plot_df_10.index.values.tolist(),plot_df_10[12].tolist(),label="SF 12",color=colors[5])

    plt.axhline(y=360, color='r', linestyle='--')
    style = dict(size=15, color='red')
    ax.text(125, 400, "1 year", **style)

    ax.set_xlim(min_number_of_sensors, max_number_of_sensors)
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.axhline(y=30, color='r', linestyle='--')
    style = dict(size=15, color='red')
    ax.text(125, 34, "1 month", **style)

    plt.axhline(y=2, color='r', linestyle='--')
    style = dict(size=15, color='red')
    ax.text(125, 2.2, "2 days", **style)

    ax.set_xlabel('Number of sensors per gateway')
    ax.set_ylabel('Time [days]')
    ax.legend(ncol=3)

    plt.savefig('./figures/lineplot-sensors-down.pdf',format='pdf',bbox_inches='tight',dpi=700)

    return 0