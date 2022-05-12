#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time, subprocess, os, signal, ast
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_rows", None, "display.max_columns", None) # Print complete dataframes

def main(): 
    SpreadingFactor = 7
    measurement_time = 6
    min_char = 20
    max_char = 480
    sleep_period = 1

    df  = pd.DataFrame({'SF': pd.Series([], dtype='int'),
                       'Char': pd.Series([], dtype='int'),
                       'Byte': pd.Series([], dtype='int'),
                       'AirTime': pd.Series([], dtype='str'),
                       'PointSize': pd.Series([], dtype='int'),
                       'MultiVal': pd.Series([], dtype='int')})


    for i in range(min_char,max_char,2):
        for SpreadingFactor in range(7,13):
            DataFilename = "./data-24-08-20/"+str(i)+"-Char"+"-"+str(SpreadingFactor)+"-SF"+"-res.txt"
            print(DataFilename)
            if os.path.isfile(DataFilename):
                print ("File exist")
                file = open(DataFilename, "r")
                contents = file.read()
                cur_file_dict = ast.literal_eval(contents)
            else:
                print ("File not exist")
    
            if (len(cur_file_dict) == 1): # TODO better approach here for multiple values in dict
                cur_AirTime = list(cur_file_dict.values())[0] 
                df.loc[len(df)] = [int(SpreadingFactor),int(i),int(i/2),int(cur_AirTime),int(SpreadingFactor)*10,5]
            if (len(cur_file_dict) > 1): # TODO better approach here for multiple values in dict
                cur_AirTime = sum(cur_file_dict.values())
                df.loc[len(df)] = [int(SpreadingFactor),int(i),int(i/2),int(cur_AirTime),int(SpreadingFactor)*10,10]

    #df.plot(x ='Char', y='AirTime', kind = 'scatter')


    fig, ax = plt.subplots(nrows=3, ncols=2,figsize=(15,10))
    fig.subplots_adjust(hspace=0.5)
    curSF = 7
    maxAirtime = df['AirTime'].max()

    for i, ax in enumerate(ax.flat):
        y = df.loc[df['SF'] == curSF]['AirTime']
        x = df.loc[df['SF'] == curSF]['Byte']
        scale = df.loc[df['SF'] == curSF]['MultiVal']*3
        ax.scatter(x, y, c='tab:blue', s=scale, label=str(curSF), alpha=1, edgecolors='none')
        ax.set(xlabel='Byte',title=f'SF{curSF}',ylabel='Airtime[ms]')
        ax.set_ylim(0,maxAirtime+1)
        curSF += 1

    #plt.show()
    plt.savefig('airtime-sf.png',bbox_inches='tight',dpi=500)

    fig, ax = plt.subplots(figsize=(10,8))
    #ax = sns.scatterplot(x="Byte", y="AirTime", size="PointSize",  alpha=0.2, palette="Set2", data=df, edgecolor='black')
    plt.scatter(df.Byte, df.AirTime, s=df.PointSize,alpha=0.2)
    plt.show()

    df.to_csv('sdr_results.csv', encoding='utf-8')

    return 0


if __name__ == '__main__':
    main()