#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 13:17:57 2023

@author: ali
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 13:30:59 2023

@author: ali
"""

import os , glob
import sys
#import nibabel as nib

data_path = '/Volumes/Data/Badea/Lab/human/ADRC/ADRC_BIDS'

list_folders_path = os.listdir(data_path)
list_of_subjs_long = [i for i in list_folders_path if 'ADRC' in i and not '.' in i]
subjects = sorted(list_of_subjs_long)
list_of_subjs = [i.replace('sub-','') for i in list_of_subjs_long]

for subj in list_of_subjs:
    #print(subj)
    #fmri_file = list_fmir_folders_path +subj + "/ses-1/func/" + subj +"_ses-1_bold.nii.gz" 
    #nib.load(fmri_file)
    python_command = "python3 /mnt/munin2/Badea/Lab/human/ADRC/ADRC_fmri_prep_pipeline/connec_fmri_prep.py "+subj
    command = python_command  
    os.system(command)