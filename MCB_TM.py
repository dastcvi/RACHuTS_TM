#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Alex St. Clair
Based on code written by Lars Kalnajs

To use this script to process data files call:

    python3 MCB_TM.py file_name1 file_name2 ...

The resulting CSVs will be placed in the directory Processed_Data/
"""

import csv 
import xml.etree.ElementTree as ET 
import struct
import time
from datetime import datetime
import sys
import os

# Results directory
RESULTS_DIR = 'Processed_Data'

# ADC -> Current conversion constants
SENSE_CURR_SLOPE = 11700
MAX_ADC_READ = 4095
VREF = 3.196
I_OFFSET = 0.00018
PULLDOWN_RESISTOR = 2000
SUPPLY_VOLT_DIV = 0.102

def readTMfile(TMfile,base_directory,lines):
    with open(base_directory + '/' + TMfile, 'rb') as TM_file:
        header = [next(TM_file).decode() for x in range(lines)]
        TM_file.readline()
        data = TM_file.readlines()

    return ''.join(header), b''.join(data)

def readDataFile(TMfile, base_directory):
    with open(base_directory + '/' + TMfile, 'rb') as TM_file:
        data = TM_file.readlines()

    return b''.join(data)

def parseXML(xmlstring): 
  
    # create element tree object 
    root = ET.fromstring(xmlstring) 
    
    #create a dictionary to store the tags
    
    XMLdict = dict()
  
    for child in root:
        value = root.find(child.tag).text
        XMLdict[child.tag] = value
      
    # return the dict
    return XMLdict


def parseMCBData(file_name, base_directory, data):
    csv_name = base_directory + '/' + RESULTS_DIR + '/' + file_name[:-3] + 'csv'

    if (os.path.exists(csv_name)):
        print('Warning: already parsed, skipping')
        return

    data_length = len(data)

    # Make sure we have a valid number of packets in the data
    if ((data_length - 4) % 32 != 0):
        print("Invalid data length, contains " + str(int((data_length-4) / 32)) + " packets")
        return
    else:
        num_packets = int((data_length-4) / 32)

    # read the header (time in seconds since standard epoch)
    profile_start = struct.unpack_from('>I',data,0)[0]

    print("Start time:   " + str(profile_start))
    print('Data length:  ' + str(data_length))
    print("Num packets:  " + str(num_packets))

    with open(csv_name, mode='w') as csv_file:
        # create a header for the CSV file
        header = ['Elapsed Time', 'Reel Torque Avg', 'Reel Torque Max', 'LW Torque Avg', 'LW Torque Max', 'Reel Curr Avg', 
                  'Reel Curr Max', 'LW Curr Avg', 'LW Curr Max', 'Differential Reel Speed', 'Reel Position', 
                  'LW Position', 'Enum', 'Reel Temp Avg', 'Reel Temp Max', 'LW Temp Avg', 'LW Temp Max', 'MC1 Temp Avg', 
                  'MC1 Temp Max', 'MC2 Temp Avg', 'MC2 Temp Max', 'Brake Curr Avg', 'Brake Curr Max', 'Supply Volt Avg', 
                  'Supply Volt Max']
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Start time (s)', profile_start])
        csv_writer.writerow(['Start time (UTC)', datetime.fromtimestamp(profile_start).strftime('%Y-%m-%d %H:%M:%S')])
        csv_writer.writerow(header)

        # parse all of the packets
        packet_start_index = 4
        for itr in range(num_packets):
            packet_data = ['-']*25
            
            packet = struct.unpack_from('>BHBHHHHHHHHHHff',data,packet_start_index+itr*32)

            # make sure the sync byte is valid
            if packet[0] != 0xA5:
                print("Bad sync, packet #" + itr+1)
                continue # skip to next packet

            # get the regular TM
            packet_data[0] = packet[1]/10.0 # ellapsed time
            packet_data[1] =  0 if (0 == packet[5]) else(packet[5] - 30000)/10.0 # reel torque avg
            packet_data[2] =  0 if (0 == packet[6]) else(packet[6] - 30000)/10.0 # reel torque max
            packet_data[3] =  0 if (0 == packet[7]) else(packet[7] - 30000)/10.0 # lw torque avg
            packet_data[4] =  0 if (0 == packet[8]) else(packet[8] - 30000)/10.0 # lw torque max
            packet_data[5] = SENSE_CURR_SLOPE * ((VREF/PULLDOWN_RESISTOR) * (packet[9]/MAX_ADC_READ) - I_OFFSET) # reel curr avg
            packet_data[6] = SENSE_CURR_SLOPE * ((VREF/PULLDOWN_RESISTOR) * (packet[10]/MAX_ADC_READ) - I_OFFSET) # reel curr max
            packet_data[7] = SENSE_CURR_SLOPE * ((VREF/PULLDOWN_RESISTOR) * (packet[11]/MAX_ADC_READ) - I_OFFSET) # lw curr avg
            packet_data[8] = SENSE_CURR_SLOPE * ((VREF/PULLDOWN_RESISTOR) * (packet[12]/MAX_ADC_READ) - I_OFFSET) # lw curr max
            if (itr > 0):
                packet_data[9] = (packet[13] - last_reel_pos) / (packet_data[0] - last_time) * 60
            packet_data[10] = packet[13] # reel position
            packet_data[11] = packet[14] # lw position

            # update tracking variables
            last_reel_pos = packet[13]
            last_time = packet_data[0]

            # get the rotating TM
            packet_data[12] = packet[2]
            if (0 == packet[2]): # reel temp
                packet_data[13] = 0 if (0 == packet[3]) else (packet[3] - 30000)/10.0
                packet_data[14] = 0 if (0 == packet[4]) else (packet[4] - 30000)/10.0
            elif (1 == packet[2]): # lw temp
                packet_data[15] = 0 if (0 == packet[3]) else (packet[3] - 30000)/10.0
                packet_data[16] = 0 if (0 == packet[4]) else (packet[4] - 30000)/10.0
            elif (2 == packet[2]): # mc1 temp
                packet_data[17] = 0 if (0 == packet[3]) else (packet[3] - 30000)/10.0
                packet_data[18] = 0 if (0 == packet[4]) else (packet[4] - 30000)/10.0
            elif (3 == packet[2]): # mc2 temp
                packet_data[19] = 0 if (0 == packet[3]) else (packet[3] - 30000)/10.0
                packet_data[20] = 0 if (0 == packet[4]) else (packet[4] - 30000)/10.0
            elif (4 == packet[2]): # brake curr
                packet_data[21] = packet[3]
                packet_data[22] = packet[4]
            elif (5 == packet[2]): # supply voltage
                packet_data[23] = VREF * (packet[3]/MAX_ADC_READ) / SUPPLY_VOLT_DIV
                packet_data[24] = VREF * (packet[4]/MAX_ADC_READ) / SUPPLY_VOLT_DIV

            csv_writer.writerow(packet_data)

    print('Results in:   ' + csv_name)


def processMCBwXML(file_name, base_directory):
    print('---- Processing ' + base_directory + '/' + file_name + ' ----')
    XMLstring, data = readTMfile(file_name,base_directory,7)
    XMLvals = parseXML(XMLstring)
    print('Status:       ' + XMLvals['StateFlag1'])
    print('Message:      ' + XMLvals['StateMess1'])
    parseMCBData(file_name, base_directory, data[5:-5])
    print('')

def processMCBwoXML(file_name, base_directory):
    print('---- Processing ' + base_directory + '/' + file_name + ' ----')
    data = readDataFile(file_name, base_directory)
    parseMCBData(file_name, base_directory, data)

def main():
    num_args = len(sys.argv)

    # process each specified file
    for itr in range(num_args - 1):
        # make sure the results directory exists for the file
        base_directory, file_name = sys.argv[itr+1].rsplit('/',1)
        results_directory = base_directory + '/' + RESULTS_DIR + '/'

        if not os.path.exists(base_directory + '/' + RESULTS_DIR + '/'):
            os.mkdir(base_directory + '/' + RESULTS_DIR)

        processMCBwXML(file_name, base_directory)
      
if __name__ == "__main__": 
  
    # calling main function 
    main() 