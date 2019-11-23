#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interface aimed at dowloading Strateole-2 files on the CCMz.
This interface uses python pysftp module.
"""

import datetime as dt
import os
import glob
import pysftp
import shutil
import gzip
from zipfile import ZipFile
#https://pysftp.readthedocs.io/en/latest/pysftp.html

# Some constant values
from retrieve_st2_data_cfg import *

def mirror_ccmz_folder(ccmz_folder, local_target_dir=default_local_target_dir, show_individual_file=True):
   """
   Mirror one CCMz folder.
   Files are stored locally in local_target_dir/ccmz_path/to/ccmz_folder/
   Files already downloaded are not downloaded again.
   local_target_dir prescribes where CCMz files will be downloaded locally.
   show_individual_file controls whether the name of each downloaded file is displayed or not.
   """

   print('---------------------------------')
   print('Trying to mirror CCMz folder: \033[1m'+ccmz_folder+'\033[0m')

   # Create (if needed) the appropriate local directory
   local_folder=os.path.join(local_target_dir,ccmz_folder)
   if not os.path.exists(local_folder):
      os.makedirs(local_folder)

   # Connect to CCMz
   cnopts = pysftp.CnOpts()
   cnopts.hostkeys = None
   with pysftp.Connection(host=ccmz_url, username=ccmz_user, password=ccmz_pass, cnopts=cnopts) as sftp:
       print("\033[1mConnection to CCMz succesfully established\033[0m...")

       # Switch to the remote directory
       try:
           sftp.cwd(ccmz_folder)
       except IOError:
           print('\033[1m\033[91mNo such directory on CCMz: '+ccmz_folder+'\033[0m')
           return

       # Get file list in current directory, i.e. those that have been already downloaded from CCMz
       local_files=glob.glob(os.path.join(local_folder,'*')) # filenames with relative path
       local_filenames=[os.path.basename(f) for f in local_files] # filenames without

       # Get file list from the CCMz directory with file attributes
       ccmz_file_list = sftp.listdir_attr()

       # check wether CCMz files need to be downloaded
       n_downloads=0
       for ccmz_file in ccmz_file_list:
           # Get rid of directories in CCMZ folder (if any)
           if ccmz_file.longname[0] == '-':
               ccmz_filename=ccmz_file.filename
               # Check whether the file has already been downloaded (so as to not download it again)
               if not ccmz_filename in local_filenames:
                  # file has to be downloaded
                  if show_individual_file == True:
                      print('Downloading \033[92m'+ccmz_filename+'\033[0m...') # display file name
                  sftp.get(ccmz_filename,os.path.join(local_folder,ccmz_filename),preserve_mtime=True)
                  n_downloads=n_downloads+1

                  # move the file to the correct day's directory
                  zippath = os.path.join(local_folder,ccmz_filename)
                  print (zippath)
                  _, filedate, _, _, _ = ccmz_filename.rsplit('_',4)
                  fileyear = filedate[2:4]
                  filemonth = filedate[4:6]
                  fileday = filedate[6:8]
                  newdirectory = default_local_target_dir + '/' + 'FullTM_' + filemonth + '-' + fileday + '-' + fileyear
                  if not os.path.exists(newdirectory + '/'):
                     os.mkdir(newdirectory)
                  datafilepath = newdirectory + '/' + ccmz_filename
                  shutil.copyfile(zippath,datafilepath)
                  with gzip.open(datafilepath, 'rb') as f_in:
                     with open(datafilepath[0:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                  os.remove(datafilepath) # delete the gzip

       # and print some statistics
       if n_downloads == 0:
           print('\nYour local repository \033[92m'+local_folder+'\033[0m looks\033[1m up do date\033[0m')
       else:
           print('\n\033[1m'+str(n_downloads)+ '\033[0m file(s) downloaded in \033[92m'+local_folder+'\033[0m')


def loop_over_flights_and_instruments():
    """
    Get all data from CCMz for the input list of flights/instruments
    """
    for flight in my_flights:
        for instrument in my_instruments:
            ccmz_folder = flight + '/' + instrument + '/' + flight_or_test + '/' + tm_or_tc + '/' + raw_or_processed
            #ccmz_folder=os.path.join(flight,instrument,flight_or_test,tm_or_tc,raw_or_processed)
            #mirror_ccmz_folder(ccmz_folder)
            mirror_ccmz_folder(ccmz_folder, show_individual_file=False)


if __name__ == '__main__':
    loop_over_flights_and_instruments()
