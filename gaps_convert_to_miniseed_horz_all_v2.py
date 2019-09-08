#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:48:07 2019

@author: joseph
"""
from __future__ import division
import pandas as pd
import os
import glob
import numpy as np 
import matplotlib.pyplot as plt
import time
from datetime import datetime,timedelta
from obspy.core import Stream, Trace
from obspy import read
import datetime

dir0 = os.getcwd()


import matplotlib.pyplot as plt

add = dir0

day = add.split("/")[-1][4:7]




def format_time(x, y):
    x = x
    hr = y
    t = datetime.datetime.fromtimestamp(x)
    t = t.replace( hour = hr )
    s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
    tail = s[-7:]
    f = round(float(tail), 3)
    temp = "%.3f" % f
    return "%s%s" % (s[:-7], temp[1:])

def convert_to_mseed( file, stn, day, cha ):
       import datetime
       
       
       #dir1 = file
       #df = pd.read_csv(dir1, index_col = None)
       
       #file2 = "2019139_????00000_9558_ch1.csv"
       #file_list = os.path.join(add, file2)
       print file
       file_list = file
       appended_data = []
       for ff in sorted(glob.glob(file_list)):
           data = pd.read_csv(ff, index_col = None)
           appended_data.append(data)
       
       aa = pd.concat(appended_data)
       
       #print aa
       tstamp = aa["timestamp"]
       tstamp_values = tstamp.values
       #plt.plot(tstamp_values)
       
       aa.loc[:,"diff"] = aa["timestamp"].diff()
       
       
       #print aa["diff"]
       #aa_filtered = aa.query('diff != 4')
       #aa.query('diff != 4.0')
       aa.loc[:,"new_timestamp"] = aa["timestamp"].apply(lambda x: x/1000)
       #aa.loc[:, "new_datetime"] = aa['new_timestamp'].apply(lambda x: format_time(x))
       aa.loc[:, "new_datetime"] = aa.apply(lambda x: format_time(x["new_timestamp"], x["hour"]), axis =1 )
       #aa.loc[:, "new_datetime"] = aa['new_timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S.%f'))
       
       aa = aa.set_index('new_datetime')
       
       print aa.index[0]
       print aa.index[-1]
       start_tstamp = aa["new_timestamp"].values[0]
       end_tstamp = aa["new_timestamp"].values[-1]
       print start_tstamp, end_tstamp
       
       #tseries_np = np.arange(start_tstamp,end_tstamp,0.004)
       #print tseries_np
       
       #find where gaps are present in the data
       gaps = aa.query('diff != 4.0')
       filtered_gaps = gaps[gaps['diff'].notnull()]
       print "filtered_gaps"
       print filtered_gaps
       print "gaps"
       print gaps
       l_gaps = len(filtered_gaps)
       if l_gaps == 0:
              print "Inside no gap condition"
              g_start_ngaps = 0
              tt_end_ngaps = aa.iloc[-1].name
              tt_end_ngaps_loc = aa.index.get_loc( tt_end_ngaps )
              g_end_ngaps = tt_end_ngaps_loc
              
              tmp_ngaps = aa[ g_start_ngaps: g_end_ngaps]
              data_ngaps = tmp_ngaps[ "counts" ].values
              data_ngaps = data_ngaps.astype( 'int32' )
              
              start_time = aa.iloc[ g_start_ngaps ].name
              end_time = aa.iloc[ g_end_ngaps ].name
              sample_rate = 250
              
              net = 'TX'
              sta = str(stn)
              channel = cha
              
              
              stats = {'network': net, 'station': sta, 
                'location': '', 'channel': channel,
                'npts': len(data_ngaps),'sampling_rate': sample_rate, 
                'starttime':start_time,'endtime':end_time}
              
              st = Stream([Trace(data = data_ngaps, header = stats)])
              day = day
              tmp_fname = sta + ".NV.." + cha + ".2019." + day
              
              output_fname = tmp_fname + ".MSEED"
              output_loc = os.path.join( dir0, "mseed_files", output_fname )
              
              st.write(output_loc, format = 'MSEED')
              del st 
              
       else:
              
              
              flag = 0 
              fnum_flag = 0 # for output mseed file_names
              for i in range(l_gaps+1):
                     if flag == 0:
                            g_start = 0
                            flag = flag +1
                            print i
                            t = filtered_gaps.index.values[ i ]
                            
                            loc = aa.index.get_loc( t )
                            #gaps0_prev = aa.iloc[ loc - 1 ]
                            print aa
                            print t
                            print "loc"
                            print loc
                            #print loc.type
                            print "here2"
                            g_end = loc - 1
                            print "here3"
                     else:
                            if i > l_gaps - 1:       
                                   t_tmp = filtered_gaps.index.values[ i - 1 ] #because i is more than max l_gaps
                                   loc_tmp = aa.index.get_loc( t )
                                   t_end = aa.iloc[ -1 ].name
                                   t_end_loc = aa.index.get_loc( t_end )
                                   g_end = t_end_loc
                                   g_start = loc_tmp
                            else:
                                   t_start = filtered_gaps.index.values[ i - 1 ]
                                   loc_start = aa.index.get_loc( t )
                                   #gaps0_prev_start = aa.iloc[ loc_start ]
                                   g_start = loc_start
                                   
                                   t = filtered_gaps.index.values[ i ]
                                   loc = aa.index.get_loc( t )
                                   #gaps0_prev = aa.iloc[ loc - 1 ]
                                   g_end = loc - 1
                     
                     tmp = aa[ g_start: g_end ]
                     data = tmp["counts"].values
                     data = data.astype('int32')
                     
                     start_time = aa.iloc[g_start].name
                     end_time = aa.iloc[g_end].name
                     sample_rate = 250 
                     
                     net = 'TX'
                     sta = str(stn)
                     
                     #Dictionary required to get station names from reftek names
                     
                     
                     stats = {'network': net, 'station': sta, 
                              'location': '', 'channel': cha,
                              'npts': len(data),'sampling_rate': sample_rate, 
                              'starttime':start_time,'endtime':end_time}
                     
                     st = Stream([Trace(data = data, header = stats)])
                     day = day
                     tmp_fname = sta + ".NV.." + cha + ".2019." + day + "."
                     
                     output_fname = tmp_fname + str(fnum_flag) + ".MSEED"
                     output_loc = os.path.join( dir0, "mseed_files", output_fname )
                     
                     st.write(output_loc, format = 'MSEED')
                     fnum_flag = fnum_flag + 1

all_squadrons = ["rapier_sq1.csv","rapier_sq2.csv", "rapier_sq3.csv", "rapier_sq4.csv"]

for sqd in all_squadrons:
       
       reftek_ids = os.path.join( dir0, sqd )
       df = pd.read_csv( reftek_ids )
       #reftek_ids = os.path.join(dir0, "rapier_sq1.csv")
       
       for irefname in df.reftek.unique(): #looping through reftek names
              print irefname
              iref_loc = df["reftek"] == irefname
              sta = df.loc[ iref_loc, "new_station_id" ].values[0]
              sta = '%04d' % sta
              #add_fname = "2019139_*_" + str(irefname) + "_ch2.csv"
              
              add_fname = "2019" + day + "_*_" + str(irefname) + "_ch2.csv"
              print add_fname
              add = os.path.join( dir0, add_fname)
              add_glob = glob.glob(add)
              if len(add_glob) == 0:
                     continue
       #       if not os.path.exists( add ):
       #              continue
              cha = "EHN"       
              out = convert_to_mseed( add, sta, day, cha )       
              
