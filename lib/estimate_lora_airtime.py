#!/usr/bin/env python
# -*- coding: utf-8 -*-


LORAWAN_HEADER_SIZE = 13 # https://avbentem.github.io/lorawan-airtime-ui/ttn/eu868/10


"""
Based on the following work with minor adapations
https://github.com/tanupoo/lorawan_toa
"""

def get_toa(n_size, n_sf, n_bw=125, enable_auto_ldro=True, enable_ldro=False,
            enable_eh=True, enable_crc=True, n_cr=1, n_preamble=8, n_duty_cycle=1, enable_payload_only=False):
    '''
    Parameters:
        n_size:
            PL in the fomula.  PHY Payload size in byte (= MAC Payload + 5)
        n_sf: SF (12 to 7)
        n_bw: Bandwidth in kHz.  default is 125 kHz for AS923.
        enable_auto_ldro
            flag whether the auto Low Data Rate Optimization is enabled or not.
            default is True.
        enable_ldro:
            if enable_auto_ldro is disabled, LDRO is disable by default,
            which means that DE in the fomula is going to be 0.
            When enable_ldro is set to True, DE is going to be 1.
            LoRaWAN specification does not specify the usage.
            SX1276 datasheet reuiqres to enable LDRO
            when the symbol duration exceeds 16ms.
        enable_eh:
            when enable_eh is set to False, IH in the fomula is going to be 1.
            default is True, which means IH is 0.
            LoRaWAN always enables the explicit header.
        enable_crc:
            when enable_crc is set to False, CRC in the fomula is going to be 0.
            The downlink stream doesn't use the CRC in the LoRaWAN spec.
            default is True to calculate ToA for the uplink stream.
        n_cr:
            CR in the fomula, should be from 1 to 4.
            Coding Rate = (n_cr/(n_cr+1)).
            LoRaWAN takes alway 1.
        n_preamble:
            The preamble length in bit.
            default is 8 in AS923.
        n_duty_cycle:
            The duty cycle in percent. 
            default is 1
        enable_payload_only:
            Enables Payload only calcuations removing a static 8 
    Return:
        dict type contains below:
        r_sym: symbol rate in *second*
        t_sym: the time on air in millisecond*.
        t_preamble:
        v_ceil:
        symbol_size_payload:
        t_payload:
        t_packet: the time on air in *milisecond*.
    '''
    r_sym = (n_bw*1000.) / math.pow(2,n_sf)
    t_sym = 1000. / r_sym
    t_preamble = (n_preamble + 4.25) * t_sym
    # LDRO
    v_DE = 0
    if enable_auto_ldro:
        if t_sym > 16:
            v_DE = 1
    elif enable_ldro:
        v_DE = 1
    # IH
    v_IH = 0
    if not enable_eh:
        v_IH = 1
    # CRC
    v_CRC = 1
    if enable_crc == False:
        v_CRC = 0
 
    a = 8.*n_size - 4.*n_sf + 28 + 16*v_CRC - 20.*v_IH

    b = 4.*(n_sf-2.*v_DE)
    v_ceil = a/b

    if enable_payload_only == False:
        n_payload = 8 + max(math.ceil(a/b)*(n_cr+4), 0)
    else:
        n_payload = max(math.ceil(a/b)*(n_cr+4), 0)
    t_payload = n_payload * t_sym
    t_packet = t_preamble+ t_payload

    ret = {}
    ret["r_sym"] = r_sym
    ret["t_sym"] = t_sym
    ret["n_preamble"] = n_preamble
    ret["t_preamble"] = t_preamble
    ret["v_DE"] = v_DE
    ret["v_ceil"] = v_ceil
    ret["n_sym_payload"] = n_payload
    ret["t_payload"] = t_payload
    ret["t_packet"] = round(t_packet, 3)
    ret["phy_pl_size"] = n_size
    ret["mac_pl_size"] = n_size - LORAWAN_HEADER_SIZE # this value was previously "-5"
    ret["sf"] = n_sf
    ret["bw"] = n_bw
    ret["ldro"] = "enable" if ret["v_DE"] else "disable"
    ret["eh"] = "enable" if enable_eh else "disable"
    ret["cr"] = n_cr
    ret["preamble"] = n_preamble
    ret["duty_cycle"] = n_duty_cycle
    ret["t_cycle"] = (ret["t_packet"]/1000.)*(100./ret["duty_cycle"])
    ret["max_packets_day"] = 86400./ret["t_cycle"]

    return ret


def estimate_wide_range(recalc=False):

    if recalc:
        col_names =  ['Payload', 'SF', 'duty_cycle','t_packet','max_packets_day']
        df  = pd.DataFrame(columns = col_names)

        payload = range(6, 2000)
        spreadingfactor = range(7,13)
        dutycycle = [1]
        
        for SF in spreadingfactor:
            for p in payload:
              for d in dutycycle:
                ret = get_toa(n_size=p,n_sf=SF,n_duty_cycle=d)
                df.loc[len(df)] = [p, SF, d, ret['t_packet'],ret['max_packets_day']]
        df.to_csv('res.csv')
    else:
        df = pd.read_csv('res.csv',index_col=0)

    fig, ax = plt.subplots(figsize=(15,5))
    df[df.SF == 7].plot(x='Payload', y='max_packets_day',ax=ax,label='SF7')
    df[df.SF == 10].plot(x='Payload', y='max_packets_day',ax=ax,color='red',label='SF10')
    ax.set_xlabel('Phy Payload [Byte]')
    ax.set_ylabel('Max Packets per Day')
    ax.set_yscale('log')
    ax.set_xlim(6,2000)
    ax.set_ylim(1,30000)

    #df.groupby(['SF']).plot(x='Payload', y='max_packets_day',ax=ax)

    return ax


#SF = 7 # Spreading Factor
    #d = 1 # Duty Cycle

    #col_names =  ['ID','Layer','Payload', 'SF', 'duty_cycle','t_payload']
    #df  = pd.DataFrame(columns = col_names)
    #print(get_toa(n_size=int(LORAWAN_HEADER_SIZE+80),n_sf=9,n_duty_cycle=1)) # Debug to play arround

    #for pktID, d_protos in header_sizes.items():
    #    log.debug(f'Looking at the Paket with the ID {pktID}')
    #    cur_frame_pktSize = 0 # Add a checkout calucation 
    #    # Add calculations for LoRaWAN Header and CRD without any payload as one block
    #    ret = get_toa(n_size=int(LORAWAN_HEADER_SIZE),n_sf=SF,n_duty_cycle=d)
    #    df.loc[len(df)] = [int(pktID),'LoRaWAN',int(0+LORAWAN_HEADER_SIZE), SF, d, ret['t_packet']]
    #    for proto in d_protos:
    #        log.debug(f'Looking at the Protocol {proto} in Frame with the ID {pktID}')
    #        pktSize = d_protos[proto]
    #        cur_frame_pktSize += int(pktSize)
    #        log.debug(f'The paket size is {pktSize}')
    #        # Fill the data frame with the different protocols embedded in the pcap file but without LoRa-Header and CRC
    #        # Only use the airtime of the payload
    #        ret = get_toa(n_size=int(pktSize),n_sf=SF,n_duty_cycle=d, n_preamble=0, enable_crc=False, enable_payload_only=True, enable_auto_ldro=False, enable_eh=False)
    #        df.loc[len(df)] = [int(pktID),proto,int(pktSize), SF, d, ret['t_payload']]

        # Add a different calcuation based on the complete Frame
    #    log.debug(f"Looking at the complete frame with a paket size of {cur_frame_pktSize}")
    #    ret = get_toa(n_size=int(LORAWAN_HEADER_SIZE+cur_frame_pktSize),n_sf=SF,n_duty_cycle=d)
    #    df.loc[len(df)] = [int(pktID),'Paket-Payload',int(cur_frame_pktSize), SF, d, ret['t_packet']]
    #print(df)

    #pivot_df = df.loc[df['Layer'] != 'Paket-Payload'].pivot(index='ID', columns='Layer', values='t_payload')
    #print(pivot_df)
    #fig, ax = plt.subplots()
    #pivot_df.loc[:,['LoRaWAN','Ethernet','IP','TCP','TLS']].plot.bar(stacked=True, figsize=(10,7),ax=ax,cmap="Set1")
    #ax.set_ylabel('Airtime [ms]')

    #paketFunctions = ('SYN', 'SYN-ACK', 'ACK', 'Client-Hello', 'ACK','Server-Hello','ACK','Change Spec', 'ACK', 'Data', 'ACK', 'Data','ACK', 'Data', 'ACK', 'FIN-ACK', 'FIN-ACK','ACK')

    #ax.set_xticklabels(paketFunctions,rotation=45)

    #plt.show()

    #df.to_csv('./Results.csv')
