"""
Configuration file for retrieve_st2_data.py script
"""

default_local_target_dir="D:\\CU_Boulder\\LASP\\Stratéole\\TM" # directory where to store data on your local machine

ccmz_url="sshstr2.ipsl.polytechnique.fr" # CCMz URL from where to download data
ccmz_user="astclair" # Your login on the CCMz
ccmz_pass="j;zk8t6u" # Your password on the CCMz

# ID of flights in which I'm interested in
my_flights=['ST2_C0_03_TTL3'] # Adapt according to your needs

# ID of my instrument
my_instruments=['RACHUTS'] # Adapt according to your needs

# Flight or Test (AIT)
#flight_or_test='AIT'
flight_or_test='Flight'

# TM or TC
tm_or_tc='TM'
#tm_or_tc='TC'

# Only for TM files
# Raw (tar archives) or Processed (individual TM frames)
raw_or_processed='Processed'
#raw_or_processed='Raw'
