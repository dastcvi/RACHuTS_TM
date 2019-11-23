#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import sys
import time
from datetime import datetime


def PlotCSV(filepath):
    print('Plotting: ' + filepath)
    data = np.genfromtxt(filepath, delimiter = ',', skip_header = 3)
    time = data[:,0]

    reel_temp_indices = ~np.isnan(data[:,13])
    lw_temp_indices = ~np.isnan(data[:,15])
    mc1_temp_indices = ~np.isnan(data[:,17])
    voltage_indices = ~np.isnan(data[:,23])

    plt.figure()

    plt.subplot(3,3,1)
    plt.plot(time,data[:,1], label='Reel Torque')
    plt.plot(time,data[:,2],'r--', label='Max')
    plt.plot(time,data[:,1] - (data[:,2] - data[:,1]),'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    #plt.xlabel('Time (s)')
    plt.ylabel('Torque (N)')
    #plt.title('Reel Torque')

    plt.subplot(3,3,2)
    plt.plot(time,data[:,5], label='Reel Current')
    plt.plot(time,data[:,6],'r--', label='Max')
    plt.plot(time,data[:,5] - (data[:,6] - data[:,5]),'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    #plt.xlabel('Time (s)')
    plt.ylabel('Current (A)')
    #plt.title('Reel Current')

    plt.subplot(3,3,3)
    plt.plot(time[reel_temp_indices],data[reel_temp_indices,13], label='Reel Temp')
    plt.plot(time[reel_temp_indices],data[reel_temp_indices,14], 'r--', label='Max')
    plt.plot(time[reel_temp_indices],2*data[reel_temp_indices,13]-data[reel_temp_indices,14], 'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    #plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    #plt.title('Reel Temperature')

    plt.subplot(3,3,4)
    plt.plot(time[mc1_temp_indices],data[mc1_temp_indices,17], label='MC1 Temp')
    plt.plot(time[mc1_temp_indices],data[mc1_temp_indices,18], 'r--', label='Max')
    plt.plot(time[mc1_temp_indices],2*data[mc1_temp_indices,17]-data[mc1_temp_indices,18], 'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    #plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    #plt.title('MC1 Temperature')

    plt.subplot(3,3,5)
    plt.plot(time,data[:,7], label='LW Current')
    plt.plot(time,data[:,8],'r--', label='Max')
    plt.plot(time,data[:,7] - (data[:,8] - data[:,7]),'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    #plt.xlabel('Time (s)')
    plt.ylabel('Current (A)')
    #plt.title('LW Current')

    plt.subplot(3,3,6)
    plt.plot(time[lw_temp_indices],data[lw_temp_indices,15], label='LW Temp')
    plt.plot(time[lw_temp_indices],data[lw_temp_indices,16], 'r--', label='Max')
    plt.plot(time[lw_temp_indices],2*data[lw_temp_indices,15]-data[lw_temp_indices,16], 'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    #plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    #plt.title('LW Temperature')

    plt.subplot(3,3,7)
    plt.plot(time[voltage_indices],data[voltage_indices,23], label='Voltage')
    plt.plot(time[voltage_indices],data[voltage_indices,24], 'r--', label='Max')
    plt.plot(time[voltage_indices],2*data[voltage_indices,23]-data[voltage_indices,24], 'r--', label='Min')
    plt.legend(loc='lower right', fontsize = 'small')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    #plt.title('MC1 Temperature')

    plt.subplot(3,3,8)
    plt.plot(time,data[:,10], label='Reel Position')
    plt.legend(loc='lower right', fontsize = 'small')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (revs)')
    #plt.title('Reel Position')

    plt.subplot(3,3,9)
    plt.plot(time,data[:,11], label='LW Position')
    plt.legend(loc='lower right', fontsize = 'small')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (mm)')
    #plt.title('LW Position')

    plt.show()


if __name__ == "__main__":
    num_args = len(sys.argv)
    for itr in range(num_args-1):
        PlotCSV(sys.argv[itr+1])