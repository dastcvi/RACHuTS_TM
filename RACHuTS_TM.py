#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Alex St. Clair
Based on code written by Lars Kalnajs

To use this script to process the RACHuTS TM files:

    First run "python3 retrieve_st2_data.py"
    Then run "python3 RACHuTS_TM.py FullTM*/*.dat"

The resulting MCB CSVs and TM text will be placed in the directory FullTM*/Processed_Data/
"""

import csv
import xml.etree.ElementTree as ET
import struct
import time
from datetime import datetime
import sys
import os
import MCB_TM

# Results directory
RESULTS_DIR = 'Processed_Data'

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

def processFile(file_name, base_directory):
    with open(base_directory + '/' + RESULTS_DIR + '/messages.txt', 'a') as message_file:
        message_file.write('---- File: ' + base_directory + '/' + file_name + ' ----\n')

        XMLstring, data = readTMfile(file_name,base_directory,7)
        XMLvals = parseXML(XMLstring)

        message_file.write('Status:\t' + XMLvals['StateFlag1'] + '\n')
        message_file.write('Message ' + XMLvals['Msg'] + ':\t' + XMLvals['StateMess1'] + '\n')
        if int(XMLvals['Length']) != 0:
            message_file.write('Bytes: ' + XMLvals['Length'] + '\n')

        if 'Finished' in XMLvals['StateMess1'] or 'dock condition' in XMLvals['StateMess1']:
            MCB_TM.parseMCBData(file_name, base_directory, data[5:-5])
            message_file.write('MCB Data Parsed\n')

        message_file.write('\n')

def main():
    num_args = len(sys.argv)
    num_processed = 0

    # process each specified file
    for itr in range(num_args - 1):
        already_processed = False

        # make sure the results directory exists for the file
        base_directory, file_name = sys.argv[itr+1].rsplit('/',1)

        if not os.path.exists(base_directory + '/' + RESULTS_DIR + '/'):
            os.mkdir(base_directory + '/' + RESULTS_DIR)

        if os.path.exists(base_directory + '/' + RESULTS_DIR + '/processed_files.txt'):
            with open(base_directory + '/' + RESULTS_DIR + '/processed_files.txt', 'r') as processed_files:
                for line in processed_files:
                    if file_name in line:
                        already_processed = True

        if not already_processed:
            num_processed += 1
            processFile(file_name, base_directory)
            with open(base_directory + '/' + RESULTS_DIR + '/processed_files.txt', 'a') as processed_files:
                processed_files.write(file_name + '\n')

    with open(base_directory + '/' + RESULTS_DIR + '/messages.txt', 'a') as message_file:
        message_file.write('\n==== End of Files ====\n\n\n')

    print('-----------------------------------')
    print('Completed processing: ' + str(num_processed) + ' files')
    print('-----------------------------------')

if __name__ == "__main__":

    # calling main function
    main()