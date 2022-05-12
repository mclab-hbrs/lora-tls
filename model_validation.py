#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging as log
import ntpath
import glob
import os
import pprint
from lib.pcap_read_and_dissect import *
from lib.estimate_lora_airtime import *
from lib.results_and_plots import *
from cycler import cycler
import matplotlib.pyplot as plt

params = {
    'text.usetex': True,
    'figure.figsize': [4.5, 5.5],
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'axes.labelsize': 18,
    'legend.fontsize': 10,
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
numberOfPlottingFeatures = 6
colors = sns.color_palette("Blues", numberOfPlottingFeatures)
linestyles = ['-', '--', '-.', ':']

LORAWAN_HEADER_SIZE = 13

def calc_airtime_in_dataframe(row):
    return get_toa(n_size=int(LORAWAN_HEADER_SIZE+row['Byte']),n_sf=row['SF'])['t_packet']

def percentage_change(col1,col2):
    return ((col2 - col1) / col1) * 100

def main():
    log.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    log.getLogger('numexpr').setLevel(logging.INFO)
    log.getLogger('matplotlib').setLevel(logging.INFO)

    fragmentation_size=250
    spreading_factor = 9
    Payload_Size = 10

    sdr_data = pd.read_csv("./sdr/sdr_results.csv") 

    sdr_data['CalcAirtime'] = sdr_data.apply(calc_airtime_in_dataframe, axis=1)

    sdr_data['diffpercent'] = percentage_change(sdr_data['AirTime'],sdr_data['CalcAirtime'])    

    print(sdr_data)
    print(sdr_data['diffpercent'].mean())

    fig, ax = plt.subplots(figsize=(5,4))
    i=0

    SpreadingFactor = 7
    curSF = SpreadingFactor
    y2 = sdr_data.loc[sdr_data['SF'] == curSF]['CalcAirtime']
    y = sdr_data.loc[sdr_data['SF'] == curSF]['AirTime']
    x = sdr_data.loc[sdr_data['SF'] == curSF]['Byte']
    SF7data = ax.scatter(x, y, alpha=1, s=10, label = f'data SF{curSF}',color=colors[i])
    SF7predict = ax.scatter(x, y2, alpha=0.05, s=120, label = f'predict SF{curSF}',color='black')
    i=i+1

    SpreadingFactor = 8
    curSF = SpreadingFactor
    y2 = sdr_data.loc[sdr_data['SF'] == curSF]['CalcAirtime']
    y = sdr_data.loc[sdr_data['SF'] == curSF]['AirTime']
    x = sdr_data.loc[sdr_data['SF'] == curSF]['Byte']
    SF8data = ax.scatter(x, y, alpha=1, s=10, label = f'data SF{curSF}',color=colors[i])
    SF8predict = ax.scatter(x, y2, alpha=0.05, s=120, label = f'predict SF{curSF}',color='black')
    i=i+1

    SpreadingFactor = 9
    curSF = SpreadingFactor
    y2 = sdr_data.loc[sdr_data['SF'] == curSF]['CalcAirtime']
    y = sdr_data.loc[sdr_data['SF'] == curSF]['AirTime']
    x = sdr_data.loc[sdr_data['SF'] == curSF]['Byte']
    SF9data = ax.scatter(x, y, alpha=1, s=10, label = f'data SF{curSF}',color=colors[i])
    SF9predict = ax.scatter(x, y2, alpha=0.05, s=120, label = f'predict SF{curSF}',color='black')
    i=i+1

    SpreadingFactor = 10
    curSF = SpreadingFactor
    y2 = sdr_data.loc[sdr_data['SF'] == curSF]['CalcAirtime']
    y = sdr_data.loc[sdr_data['SF'] == curSF]['AirTime']
    x = sdr_data.loc[sdr_data['SF'] == curSF]['Byte']
    SF10data = ax.scatter(x, y, alpha=1, s=10, label = f'data SF{curSF}',color=colors[i])
    SF10predict = ax.scatter(x, y2, alpha=0.05, s=120, label = f'predict SF{curSF}',color='black')
    i=i+1

    SpreadingFactor = 11
    curSF = SpreadingFactor
    y2 = sdr_data.loc[sdr_data['SF'] == curSF]['CalcAirtime']
    y = sdr_data.loc[sdr_data['SF'] == curSF]['AirTime']
    x = sdr_data.loc[sdr_data['SF'] == curSF]['Byte']
    SF11data = ax.scatter(x, y, alpha=1, s=10, label = f'data SF{curSF}',color=colors[i])
    SF11predict = ax.scatter(x, y2, alpha=0.05, s=120, label = f'predict SF{curSF}',color='black')
    i=i+1

    SpreadingFactor = 12
    curSF = SpreadingFactor
    y2 = sdr_data.loc[sdr_data['SF'] == curSF]['CalcAirtime']
    y = sdr_data.loc[sdr_data['SF'] == curSF]['AirTime']
    x = sdr_data.loc[sdr_data['SF'] == curSF]['Byte']
    SF12data = ax.scatter(x, y, alpha=1, s=10, label = f'data SF{curSF}',color=colors[i])
    SF12predict = ax.scatter(x, y2, alpha=0.05, s=120, label = f'predict SF{curSF}',color='black')

    extra_label = ax.scatter([0],[0], marker = 'None', linestyle='None', label='dummy-empty')
    extra_label2 = ax.scatter([0],[0], alpha=0.2, s=120, label = f'predict SF{curSF}',color='black')

    # Zoom In
    axins = ax.inset_axes([0.05, 0.8, 0.2, 0.2])
    axins.scatter(x, y, alpha=1, s=10,color=colors[i])
    axins.scatter(x, y2, alpha=0.05, s=100,color='black')

    axins.set_xlim(60, 75)
    axins.set_ylim(3000, 3500)
    axins.set_xticklabels('')
    axins.set_yticklabels('')
    ax.indicate_inset_zoom(axins)

    ax.set(xlabel='Size [Byte]',ylabel='Airtime [ms]')

    ax.set_ylim(50,sdr_data['AirTime'].max()+1000)
    ax.set_xlim(0,sdr_data['Byte'].max()+5)
    ax.grid(True)

    plt.yscale('log')
    plt.legend([extra_label,SF7data,SF8data,SF9data,SF10data,SF11data,SF12data,extra_label,extra_label2],("Measured:", "SF7", "SF8","SF9","SF10","SF11","SF12","Modeled:",""), ncol=1, loc=4, prop={'size': 12}) # Two columns, vertical group labels

    plt.savefig('./figures/model-vs-sdr.pdf',format='pdf',bbox_inches='tight',dpi=700)

    return 0
    
if __name__== "__main__":
  main()
